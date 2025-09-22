from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from types import SimpleNamespace
from rest_framework.permissions import AllowAny
from loan_credit.models import LoanAppllication
from loan_credit.serializers import CustomerDetailsSerializer, LoanCreationRequestSerializer, LoanCreationResponseSerailizer, LoanEligibilityRequestSerializer, LoanEligibilityResponseSerializer, RegistrationSerializer, ViewAllLoanApplicationsResponse, ViewLoanApplicationResponse
from loan_credit.utils import LoanEligibilityChecker

class CustomerRegistration(APIView) :
    permission_classes = [AllowAny ,]
    def post(self , request , *args, **kwargs) :
        data = request.data

        # Set approved_limit to 36 times the monthly_salary
        data["approved_limit"] = 36 * data["monthly_income"]

        # serialize to save the data
        serializer = RegistrationSerializer(data=data)
        serializer.is_valid(raise_exception=True) 
        saved_data = serializer.save()

        # serialize the saved data to return as response
        response_data = CustomerDetailsSerializer(saved_data)
        return Response(response_data.data, status=status.HTTP_201_CREATED)
    
class CheckLoanEligibility(APIView) :
    permission_classes = [AllowAny ,]
    def post(self , request , *args, **kwargs) :
        # validate incoming request data
        request_serializer = LoanEligibilityRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        # main buisness logic for checking loan eligibility
        main_data = LoanEligibilityChecker(validated_data)
        response_data = main_data.check_loan_eligibility()

        # validate / serialize response data
        response_object = SimpleNamespace(**response_data)
        serializer = LoanEligibilityResponseSerializer(response_object)

        # return response
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CreateLoanApplications(APIView) :
    permission_classes = [AllowAny ,]
    def post(self, request , *args, **kwargs) :
        # validate incoming request data
        request_serializer = LoanEligibilityRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        validated_data = request_serializer.validated_data

        # main buisness logic for checking loan eligibility
        main_data = LoanEligibilityChecker(validated_data)
        response_data = main_data.check_loan_eligibility()

        # save the application even though user is not eligble
        data_to_save = request.data
        data_to_save["loan_approved"] = response_data["approval"]
        if response_data["approval"] :
            data_to_save["date_of_approval"] = datetime.now().date()
            data_to_save["end_date"] = datetime.now().date() + timedelta(days=30*validated_data["tenure"])

        data_to_save["interest_rate"] = response_data["interest_rate"] if not response_data["corrected_interest_rate"] else response_data["corrected_interest_rate"]

        data_to_save["monthly_installment"] = response_data["monthly_installment"]

        data_to_save["customer_id"] = validated_data["customer_id"]

        data_to_save["message"] = response_data.get("message", None)

        serializer = LoanCreationRequestSerializer(data=data_to_save)
        serializer.is_valid(raise_exception=True)
        saved_data = serializer.save()

        if not response_data["approval"]:
            saved_data.loan_id = None

        response_data = LoanCreationResponseSerailizer(saved_data)

        return Response(response_data.data, status=status.HTTP_201_CREATED)
    

class ViewLoanApplications(APIView) :
    permission_classes = [AllowAny ,]
    def get(self, request , *args, **kwargs) :
        loan_id = kwargs.get("loan_id" , None)
        if not loan_id :
            return Response({"error" : "loan_id is required"} , status=status.HTTP_400_BAD_REQUEST)
        
        loan_application = LoanAppllication.objects.filter(loan_id = loan_id , loan_approved = True).first()
        if not loan_application :
            return Response({"error" : "No Loan Application Found with this ID"} , status=status.HTTP_404_NOT_FOUND)
        
        response_data = ViewLoanApplicationResponse(loan_application)
        return Response(response_data.data, status=status.HTTP_200_OK)
    

class ViewAllLoanApplications(APIView) :
    permission_classes = [AllowAny ,]
    def get(self, request , *args, **kwargs) :
        customer_id = kwargs.get("customer_id" , None)
        if not customer_id :
            return Response({"error" : "customer_id is required"} , status=status.HTTP_400_BAD_REQUEST)
        
        loan_applications = LoanAppllication.objects.filter(customer_id = customer_id , loan_approved = True).all()
        if not loan_applications.exists() :
            return Response({"error" : "No Loan Applications Found for this Customer ID"} , status=status.HTTP_404_NOT_FOUND)
        response_data = ViewAllLoanApplicationsResponse(loan_applications , many=True)

        return Response(response_data.data, status=status.HTTP_200_OK)
    
