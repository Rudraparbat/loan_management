# In loan_credit/tests.py

from django.test import TestCase
from loan_credit.models import Customer, LoanAppllication

class CustomerModelTests(TestCase):
    """Test cases for the Customer model."""

    def test_create_customer(self):
        """
        Tests the successful creation of a Customer instance.
        """
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="1234567890",
            age=35,
            monthly_income=60000,
            approved_limit=2160000
        )
        self.assertIsNotNone(customer.customer_id)
        self.assertEqual(Customer.objects.count(), 1)

    def test_customer_str_representation(self):
        """
        Tests the __str__ method of the Customer model.
        """
        customer = Customer.objects.create(
            first_name="Jane",
            last_name="Smith",
            phone_number="9876543210",
            age=40,
            monthly_income=75000
        )
        self.assertEqual(str(customer), "Jane Smith")


class LoanApplicationModelTests(TestCase):
    """Test cases for the LoanApplication model."""

    def setUp(self):
        """
        The setUp method runs before every single test in this class.
        It's the perfect place to create objects that are needed by multiple tests.
        """
        self.customer = Customer.objects.create(
            first_name="Peter",
            last_name="Jones",
            phone_number="5555555555",
            age=28,
            monthly_income=45000
        )

    def test_generate_loan_id_for_first_loan(self):
        """
        Tests that the first loan created gets the default ID of 1000.
        """
        # We know the database is empty for this test because TestCase
        # creates a fresh database for each test run.
        first_loan = LoanAppllication.objects.create(
            customer_id=self.customer,
            loan_amount=10000,
            tenure=12,
            interest_rate=8.5
        )
        self.assertEqual(first_loan.loan_id, 1000)

    def test_generate_loan_id_for_subsequent_loan(self):
        """
        Tests that the second loan created gets an ID of the last one + 1.
        """
        # The first loan will get ID 1000, thanks to the generate_loan_id default
        LoanAppllication.objects.create(
            customer_id=self.customer,
            loan_amount=5000,
            tenure=6,
            interest_rate=9.0
        )

        # Now, create the second loan
        second_loan = LoanAppllication.objects.create(
            customer_id=self.customer,
            loan_amount=20000,
            tenure=24,
            interest_rate=10.0
        )
        # Its ID should be 1000 + 1
        self.assertEqual(second_loan.loan_id, 1001)

    def test_loan_application_str_representation(self):
        """
        Tests the __str__ method of the LoanApplication model.
        """
        loan = LoanAppllication.objects.create(
            customer_id=self.customer,
            loan_amount=15000,
            tenure=18,
            interest_rate=7.5
        )
        expected_str = f"Application {loan.loan_id} for Peter Jones"
        self.assertEqual(str(loan), expected_str)

