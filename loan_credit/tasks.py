# In core/management/commands/ingest_data.py

import os
import pandas as pd

from credit_approver import settings
from celery import shared_task
from celery.signals import worker_ready
from loan_credit.models import Customer, LoanAppllication # Make sure to import your models from your app

"""
This module defines a Celery task to ingest customer and loan data from specified Excel files into the database.
"""
    # 'Ingests customer and loan data from specified Excel files into the database.'

@shared_task    
def injest_data(*args, **options):
    """
    The main logic of the command. This is where the data ingestion happens.
    """
    customers_path = os.path.join(settings.BASE_DIR, 'customer_data.xlsx')
    loans_path = os.path.join(settings.BASE_DIR, 'loan_data.xlsx')
        
    print(f'Starting data ingestion from {customers_path} and {loans_path}')

    try:
            # --- 1. Ingest Customer Data ---
        print('Reading customer data...')
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
        print(f'Bulk created {len(customer_to_create)} customer records.')
        # --- 2. Ingest Loan Data ---
        print('Reading loan data...')
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
        print(f'Bulk created or ignored {len(loans_to_create)} loan records.')

    except FileNotFoundError as e:
            print(f'Error: A file was not found. Please check paths. {e}')
    except KeyError as e:
            print(f'Error: A column name in the Excel file is incorrect. Missing column: {e}')
    except Exception as e:
            print(f'An unexpected error occurred: {e}')

@worker_ready.connect
def run_initial_ingestion_on_startup(sender, **kwargs):
    """
    This function is connected to the worker_ready signal.
    It runs once when the Celery worker is fully started and ready.
    """
    print("Worker is ready. Checking for initial data...")
    # Check if any customers exist.
    if not Customer.objects.exists():
        print("Initial data not found. Dispatching ingestion task to background.")
        # Dispatch the task to be run by this worker.
        injest_data.delay()
    else:
        print("Initial data already exists. No task dispatched.")
