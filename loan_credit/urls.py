
from django.contrib import admin
from django.urls import path 
from loan_credit import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/' , views.CustomerRegistration.as_view() , name="register"),
    path('check-eligibility/' , views.CheckLoanEligibility.as_view() , name="check_eligibility"),
    path('create-loan/' , views.CreateLoanApplications.as_view() , name="create_loan_application"),
    path('view-loan/<int:loan_id>/' , views.ViewLoanApplications.as_view() , name="view_loan_application"),  
    path('view-loans/<int:customer_id>/' , views.ViewAllLoanApplications.as_view() , name="view_all_loan_application"), 
]
