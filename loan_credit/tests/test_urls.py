# In loan_credit/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from loan_credit.models import Customer, LoanAppllication
from decimal import Decimal

class URLTests(TestCase):
    """Test cases for the urls.py file."""

    def setUp(self):
        """
        Set up the necessary objects for the tests. This method runs
        before every test function in this class.
        """
        self.client = Client()
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="Customer",
            phone_number="1112223333",
            age=30,
            monthly_income=80000
        )
        self.approved_loan = LoanAppllication.objects.create(
            customer_id=self.customer,
            loan_amount=50000,
            tenure=12,
            interest_rate=10,
            loan_approved=True
        )

    def test_register_url(self):
        """
        Tests the /register/ URL.
        """
        url = reverse('register')
        data = {
            "first_name": "New",
            "last_name": "User",
            "age": 25,
            "monthly_income": 50000,
            "phone_number": "1234567890"
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_check_eligibility_url(self):
        """
        Tests the /check-eligibility/ URL.
        """
        url = reverse('check_eligibility')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_loan_url(self):
        """
        Tests the /create-loan/ URL.
        """
        url = reverse('create_loan_application')
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 150000,
            "interest_rate": 11,
            "tenure": 24
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_view_loan_url_success(self):
        """
        Tests the /view-loan/<loan_id>/ URL with a valid ID.
        """
        # Use reverse() to build the URL with the loan_id
        url = reverse('view_loan_application', args=[self.approved_loan.loan_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_loan_url_not_found(self):
        """
        Tests the /view-loan/<loan_id>/ URL with an invalid ID.
        """
        # A loan ID that does not exist
        url = reverse('view_loan_application', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_all_loans_url_success(self):
        """
        Tests the /view-loans/<customer_id>/ URL with a valid customer.
        """
        url = reverse('view_all_loan_application', args=[self.customer.customer_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The response should be a list
        self.assertIsInstance(response.json(), list)

    def test_view_all_loans_url_not_found(self):
        """
        Tests the /view-loans/<customer_id>/ URL with a customer that has no loans.
        """
        # Create a new customer with no loans
        customer_no_loans = Customer.objects.create(
            first_name="No",
            last_name="Loans",
            phone_number="4445556666",
            age=40,
            monthly_income=100000
        )
        url = reverse('view_all_loan_application', args=[customer_no_loans.customer_id])
        response = self.client.get(url)
        # Your view returns 404 if no loans are found, so we test for that.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

