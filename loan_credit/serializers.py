from loan_credit.models import Customer, LoanAppllication
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Customer
        fields = '__all__'


class CustomerDetailsSerializer(serializers.ModelSerializer) :
    name = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = [
            'customer_id',
            'name',  
            'phone_number',
            'age',
            'monthly_income',
            'approved_limit',
        ]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    

class LoanEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(write_only=True)
    loan_amount = serializers.FloatField(min_value=1.0, write_only=True)
    interest_rate = serializers.FloatField(min_value=0.0, write_only=True)
    tenure = serializers.IntegerField(min_value=1, write_only=True)

    def validate_customer_id(self, value):
        """
        Check that the customer exists in the database.
        """
        if not Customer.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Customer with this ID does not exist.")
        return value


class LoanEligibilityResponseSerializer(serializers.Serializer):

    customer_id = serializers.IntegerField(read_only=True)
    approval = serializers.BooleanField(read_only=True)
    interest_rate = serializers.FloatField(read_only=True)
    corrected_interest_rate = serializers.FloatField(read_only=True)
    tenure = serializers.IntegerField(read_only=True)
    monthly_installment = serializers.FloatField(read_only=True)


class LoanCreationRequestSerializer(serializers.ModelSerializer):
    class Meta :
        model = LoanAppllication
        fields = '__all__'



class LoanCreationResponseSerailizer(serializers.Serializer):
    
    loan_id = serializers.IntegerField(required=False, allow_null=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    loan_approved = serializers.BooleanField()
    message = serializers.CharField(allow_null = True)
    monthly_installment = serializers.FloatField()

    class Meta:
        read_only_fields = [
            'loan_id', 
            'customer_id', 
            'loan_approved', 
            'message', 
            'monthly_installment'
        ]


class CustomerDetailsResponse(serializers.ModelSerializer):
    class Meta :
        model = Customer
        fields = [
            'customer_id',
            'first_name',
            'last_name'  ,
            'phone_number',
            'age',
        ]
class ViewLoanApplicationResponse(serializers.ModelSerializer):
    customer = CustomerDetailsResponse(source='customer_id', read_only=True)

    class Meta:
        model = LoanAppllication
        fields = [
            'loan_id',
            'customer',
            'loan_amount',
            'interest_rate',
            'monthly_installment',
            'tenure'
        ]
        read_only_fields = fields


class ViewAllLoanApplicationsResponse(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()
    class Meta:
        model = LoanAppllication
        fields = [
            'loan_id',
            'loan_amount',
            'interest_rate',
            'monthly_installment',
            'repayments_left',
        ]
        read_only_fields = fields

    def get_repayments_left(self, obj):
        total_repayments = obj.tenure
        repayments_made = obj.emis_paid_on_time or 0
        return total_repayments - repayments_made
