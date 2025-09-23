# In core/management/commands/ingest_data.py

import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from credit_approver import settings
from loan_credit.models import Customer, LoanAppllication # Make sure to import your models from your app

class Command(BaseCommand):
    """
    This class is the entry point for the management command.
    Django automatically finds and runs the handle() method.
    """
    help = 'Ingests customer and loan data from specified Excel files into the database.'

    @transaction.atomic # Wraps the entire operation in a single database transaction
    def handle(self, *args, **options):
        """
        The main logic of the command. This is where the data ingestion happens.
        """
        customers_path = os.path.join(settings.BASE_DIR, 'customer_data.xlsx')
        loans_path = os.path.join(settings.BASE_DIR, 'loan_data.xlsx')
        
        self.stdout.write(self.style.SUCCESS(f'Starting data ingestion from {customers_path} and {loans_path}'))

        try:
            # --- 1. Ingest Customer Data ---
            self.stdout.write('Reading customer data...')
            customer_df = pd.read_excel(customers_path)
            customer_to_create = []
            for _, row in customer_df.iterrows():
                # This will find a customer by customer_id and update it,
                # or create a new one if it doesn't exist.
                
                customer_to_create.append(Customer(
                        first_name=row['First Name'],
                        last_name=row['Last Name'],
                        age=row['Age'],
                        phone_number=row['Phone Number'],
                        monthly_income=row['Monthly Salary'],
                        approved_limit=row['Approved Limit']
                ))

            Customer.objects.bulk_create(customer_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f'Bulk created {len(customer_to_create)} customer records.'))

            # --- 2. Ingest Loan Data ---
            self.stdout.write('Reading loan data...')
            loan_df = pd.read_excel(loans_path)
            
            loans_to_create = []
            loan_ids  = []
            for _, row in loan_df.iterrows():
                loan_ids.append(row["Loan ID"])
                loans_to_create.append(
                    LoanAppllication(
                        loan_id = row["Loan ID"] ,
                        customer_id_id=row['Customer ID'],
                        loan_amount=row['Loan Amount'],
                        tenure=row['Tenure'],
                        interest_rate=row['Interest Rate'],
                        monthly_installment=row['Monthly payment'],
                        emis_paid_on_time=row['EMIs paid on Time'],
                        date_of_approval=row['Date of Approval'],
                        end_date=row['End Date'],
                        loan_approved=True
                    )
                )

            LoanAppllication.objects.bulk_create(loans_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f'Bulk created or ignored {len(loans_to_create)} loan records.'))

        except FileNotFoundError as e:
            self.stdout.write(self.style.ERROR(f'Error: A file was not found. Please check paths. {e}'))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'Error: A column name in the Excel file is incorrect. Missing column: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {e}'))
