from django.db import models

# Create your models here.

class Customer(models.Model) :
    customer_id = models.AutoField(primary_key=True)
    first_name  = models.CharField(max_length= 50)
    last_name = models.CharField(max_length= 50)
    phone_number = models.IntegerField()
    age = models.IntegerField()
    monthly_income = models.IntegerField()
    approved_limit = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name }"
    


def generate_loan_id():
    """
    Generates a new unique loan_id by finding the last one and adding 1.
    """
    last_loan = LoanAppllication.objects.all().order_by('loan_id').last()
    if not last_loan:
        # If no loans exist yet, start from a base number like 1000
        return 1000
    
    new_loan_id = last_loan.loan_id + 1
    return new_loan_id


class LoanAppllication(models.Model):
    loan_id = models.IntegerField(primary_key=True, default=generate_loan_id)
    customer_id = models.ForeignKey(Customer ,on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_installment = models.FloatField(null=True , blank= True)
    emis_paid_on_time = models.IntegerField(null= True , blank= True , default=0)
    date_of_approval = models.DateField(null= True ,blank= True)
    end_date  = models.DateField(null= True ,blank= True)
    loan_approved = models.BooleanField(default=False)
    message = models.CharField(max_length= 255 , null= True , blank= True)  

    # for tracking loan application creation date and update date
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Application {self.loan_id} for {self.customer_id.first_name} {self.customer_id.last_name}"

