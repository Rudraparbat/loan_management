from .models import Customer , LoanAppllication
from rest_framework.response import Response
from django.db.models import Count, Sum, Q, F, IntegerField, FloatField, Value
from django.db.models.functions import Cast, Coalesce
import datetime as dt
from rest_framework import status
from datetime import datetime
from .models import Customer

class LoanEligibilityChecker :
    def __init__(self , customer_data : dict) :
        self.customer_data = customer_data
        self.customer_id = customer_data.get('customer_id')
        self.loan_amount = customer_data.get('loan_amount') 
        self.tenure = customer_data.get('tenure')
        self.current_interest_rate = customer_data.get('interest_rate')
        self.current_year = datetime.now().year
        self.today = dt.date.today()
        self.message = None

    def check_loan_eligibility(self) -> dict:
        """
        Check if a customer is eligible for a loan based on their details and the requested loan parameters.
        
        Args:
            customer (Customer): The customer applying for the loan.
            loan_amount (float): The amount of loan requested.
            interest_rate (float): The interest rate for the loan.
            tenure (int): The tenure of the loan in months.
            
        Returns:
            dict: A dictionary containing the eligibility status and other relevant details.
        """
        filter_approved = Q(loanappllication__loan_approved=True)
        customer_metrics = Customer.objects.filter(pk=self.customer_id).annotate(
        # No of loans taken in past
        num_loans_taken=Count('loanappllication', filter=filter_approved),

        # current total loan amount
        current_loan_sum=Coalesce(
                Sum(
                    'loanappllication__loan_amount',
                    # Filter for loans that are currently active
                    filter=(Q(loanappllication__end_date__gte=self.today) | Q(loanappllication__end_date__isnull=True)) & filter_approved
                ),
                Value(0, output_field=FloatField()) 
            ),
        # total emis currently paying 

        total_current_emis=Coalesce(
            Sum(
                'loanappllication__monthly_installment',
                # This filter is crucial: it ensures we only sum EMIs for active loans
                filter=(Q(loanappllication__end_date__gte=self.today) | Q(loanappllication__end_date__isnull=True)) & filter_approved
            ),
            Value(0, output_field=FloatField())  # Default to 0 if there are no active loans
        ),

        # Loan activity in current year
        loan_activity_current_year=Count(
            'loanappllication',
            filter=Q(loanappllication__date_of_approval__year=self.current_year) & filter_approved
        ),

        # How much Loan is approved 
        loan_approved_volume=Sum('loanappllication__loan_amount', filter=filter_approved),

        # Count number of  loans fully paid on time
        num_loans_fully_paid=Count(
            'loanappllication',
            filter=Q(loanappllication__emis_paid_on_time__gte=F('loanappllication__tenure')) & filter_approved
        ),

        # Total EMIs paid on time across all loans
        total_emis_paid=Sum(Cast('loanappllication__emis_paid_on_time', output_field=IntegerField()), filter=filter_approved),

        # Total tenure in months across all loans
        total_tenure_months=Sum(Cast('loanappllication__tenure', output_field=IntegerField()), filter=filter_approved),
    )

        result = customer_metrics.first()

        if not result :
            return Response({"error": "Customer not found or No Loan Data Available For This Customer"}, status=status.HTTP_404_NOT_FOUND)
        
        # calculate credit score
        credit_score = self.calculate_credit_score(result)
        print(credit_score)
        # check eligibility upon credit score calculation
        eligibility_data =  self.create_eligibiliy_data(credit_score , result)

        # determine final interest rate based on eligibility
        if eligibility_data["approved"] :
            interest_rate = eligibility_data["new_interest_rate"] if eligibility_data["new_interest_rate"] else self.current_interest_rate
        else :
            interest_rate = self.current_interest_rate

        # calculate monthly installment
        installment_amount = self.calculate_monthly_installment(interest_rate)

        # create a valid respose data upon eligibility check , credit score and installment calculation
        return self.create_response_data(eligibility_data , installment_amount)

    def calculate_credit_score(self , customer_data) -> int:
        """
        Calculates a credit score out of 100 based on aggregated customer loan data.
        """
            
        # --- Immediate Failure on Exceeding Limit ---
        if customer_data.current_loan_sum > customer_data.approved_limit:
            self.message = "Your Total Ongoing Loans Exceed Your Approved Limit"
            return 0
        
        if self.loan_amount > customer_data.approved_limit:
            self.message = "Your Asked Loan Amount Exceed Your Approved Limit"
            return 0 

        # --- NEW: Handle Case for Customers with No Loan History ---
        if customer_data.num_loans_taken == 0:
            # A customer with no loans has no payment history to judge.
            # Assigning a neutral score is standard practice.
            # A 0 would be punitive; 100 would be overly optimistic.
            return 75  # Return a default, neutral score and exit the function.

        # --- Standard Scoring Logic only runs if the customer has loans ---
        total_loans = customer_data.num_loans_taken
        fully_paid_loans = customer_data.num_loans_fully_paid or 0
        total_emis_paid = customer_data.total_emis_paid or 0
        total_emis_due = customer_data.total_tenure_months   or 0
       

        print(total_loans, fully_paid_loans, total_emis_due, total_emis_paid)

        #  Payment Performance Score (70 points)
        payment_ratio = (total_emis_paid / total_emis_due) if total_emis_due > 0 else 1
        payment_performance_score = payment_ratio * 70
        print(payment_performance_score)
        #  Loan Completion Score (30 points)
        completion_ratio = fully_paid_loans / total_loans
        loan_completion_score = completion_ratio * 30

        print(loan_completion_score)

        #  Final Score
        final_score = payment_performance_score + loan_completion_score
        return int(max(0, min(100, final_score)))


    def create_eligibiliy_data(self , credit_score : int , customer_data) -> dict :
        data = {
            "credit_score": credit_score,
            "approved" : False ,
            "current_interest_rate" : None,
            "new_interest_rate" : None,
            "message" : None
        }
        # base case to check if the current emis are greater than 50% of monthly salary 
        if customer_data.total_current_emis > (0.5 * customer_data.monthly_income) :
            self.message = "Current EMIs exceed 50% of Monthly Income"
            return data
        
        if credit_score == 0 :
            return data
        
        # Implies Interset Rate As per Customer Data
        if credit_score > 50 :
            data["approved"] = True
            return data

        elif 50 > credit_score > 30 :
            data["approved"] = True
            data["new_interest_rate"] = 12
            return data
        
        elif 30 > credit_score > 10 :
            data["approved"] = True
            data["new_interest_rate"] = 16
            return data
        
        self.message = "Credit Score is Too Low TO Approve The Loan , You may not paid your previous EMIs on time"
        return data


    def calculate_monthly_installment(self , annual_interest_rate) -> float:
        """
        Calculates the monthly installment (EMI) for a loan using the standard formula.

        Args:
            principal (float): The total principal amount of the loan.
            annual_interest_rate (float): The annual interest rate as a percentage (e.g., enter 12 for 12%).
            tenure_months (int): The loan tenure in number of months.

        Returns:
            float: The calculated monthly installment amount, rounded to 2 decimal places.
            
        Raises:
            ValueError: If the tenure is zero or negative.
        """
        if self.tenure <= 0:
            raise ValueError("Loan tenure must be a positive number of months.")
            
        if self.loan_amount < 0:
            raise ValueError("Principal amount cannot be negative.")

        # --- Calculation ---
        
        # If the interest rate is 0, EMI is just the principal divided by tenure
        if annual_interest_rate == 0:
            return round(self.loan_amount / self.tenure, 2)

        # Convert the annual interest rate from a percentage to a monthly decimal
        # For example, 12% per year becomes (12 / 12 / 100) = 0.01 per month
        monthly_interest_rate = annual_interest_rate / (12 * 100)
        
        # The standard EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        # where:
        # P = Principal
        # r = monthly interest rate
        # n = tenure in months
        
        numerator = self.loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** self.tenure
        denominator = (1 + monthly_interest_rate) ** self.tenure - 1
        
        emi = numerator / denominator
        
        return round(emi, 2)
    
    def create_response_data(self , eligibility_data : dict , installment_amount : float) -> dict :
        response_data = {
            'customer_id': self.customer_id,
            'approval': eligibility_data["approved"],
            'interest_rate': self.current_interest_rate, 
            'corrected_interest_rate': self.current_interest_rate if not eligibility_data["new_interest_rate"] else eligibility_data["new_interest_rate"],
            'tenure': self.tenure,
            'monthly_installment': installment_amount ,
            "message" : self.message
        }
        return response_data


