# Loan Management System API

This project is a comprehensive, containerized backend system for a loan management service, built with the Django REST Framework. It provides a full suite of APIs for customer registration, loan eligibility checks, loan application processing, and viewing loan details.

The entire system is orchestrated using Docker Compose, featuring a robust, production-ready architecture that includes a web server, a background task processor, a database, and a message broker.

## Core Technologies

The project is built with a modern, scalable technology stack:

- **Backend Framework:** Django & Django REST Framework
- **Database:** PostgreSQL
- **Asynchronous Tasks:** Celery
- **Message Broker & Cache:** Redis
- **Containerization:** Docker & Docker Compose
- **Web Server:** Python Development Server(For Testing)

## Features

- **Customer Registration:** Onboard new customers and automatically calculate their credit approval limit.
- **Loan Eligibility Check:** An endpoint to check if a customer is eligible for a loan based on their credit score, loan history, and current debt.
- **Loan Application:** A dedicated endpoint to create a new loan application. It saves all applications, regardless of eligibility, and assigns a `loan_id` only to approved loans.
- **View Individual Loan:** Retrieve detailed information for a specific loan application by its `loan_id`.
- **View All Customer Loans:** Retrieve a list of all loan applications associated with a specific customer.
- **Automatic Data Seeding:** On the very first run, a background task automatically populates the database with initial customer and loan data from provided Excel files.

## System Architecture

The application is designed as a multi-container system orchestrated by Docker Compose, ensuring a clean separation of concerns and easy scalability.

1.  **`app` (Django/Gunicorn):** The main web service that runs the Django REST Framework application via a Gunicorn server. It handles all incoming API requests and runs database migrations on startup.
2.  **`db` (PostgreSQL):** A dedicated container for the PostgreSQL database, which persists all application data in a Docker volume.
3.  **`redis` (Redis):** A fast, in-memory key-value store that serves as the message broker for Celery.
4.  **`worker` (Celery):** A separate container that runs the Celery worker process. It listens for tasks on the Redis queue and executes them in the background, such as the initial data seeding .

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You must have the following software installed on your system:

-   Docker ([Install Docker](https://docs.docker.com/get-docker/))
-   Docker Compose ([Included with Docker Desktop](https://docs.docker.com/compose/install/))

### Installation & Setup

1.  **Clone the repository:**
    ```
    git clone https://github.com/Rudraparbat/loan_management.git
    cd loan_management
    ```

2.  **Place the data files:**
    Ensure your initial data files, `customers.xlsx` and `loans.xlsx`, are present in the project's root directory. The system is designed to automatically ingest them on the first run.

3.  **Build and run the containers:**
    Use Docker Compose to build the images and start all the services in detached mode. The `--build` flag is important for the first run to ensure the Docker images are created correctly.
    ```
    docker-compose up --build 
    ```

4.  **Create Super User:**
    After running the container , in cmd create super user data , and can access admin page at http://localhost:8000/admin
    ```
    docker-compose exec app python manage.py createsuperuser
    ```

4.  **Run Test Cases (Not Properly Done):**
    After running the container , in cmd Run this command
    ```
    docker-compose exec app python manage.py test
    ```

5.  **View the logs (optional):**
    To see the logs from all running containers and confirm that everything has started correctly, you can run:
    ```
    docker-compose logs -f
    ```
    You should see the Django development server start on port 8000 and the Celery worker become ready.

The API will now be accessible at http://localhost:8000/.

## API Endpoints

| Endpoint                      | Method | Description                               |
| :---------------------------- | :----- | :---------------------------------------- |
| `api/register/`                  | `POST` | Registers a new customer.                 |
| `api/check-eligibility/`         | `POST` | Checks loan eligibility for a customer.   |
| `api/create-loan/`               | `POST` | Creates a new loan application.           |
| `api/view-loan/<int:loan_id>/`     | `GET`  | Retrieves details for a specific loan.    |
| `api/view-loans/<int:customer_id>/`| `GET`  | Retrieves all loans for a specific customer.|

## API Endpoints and Request Bodies

| Endpoint | Method | Request Body | Description |
| :------- | :----- | :---------- | :---------- |
| `api/register/` | `POST` | ```json
{
    "first_name": "Rudra",
    "last_name": "Singh",
    "age": 23,
    "monthly_income": 23000,
    "phone_number": 8697989224
}
``` | Register a new customer |
| `api/check-eligibility/` | `POST` | ```json
{
    "customer_id": 230,
    "loan_amount": 120030,
    "interest_rate": 8.12,
    "tenure": 12
}
``` | Check loan eligibility |
| `api/create-loan/` | `POST` | ```json
{
    "customer_id": 230,
    "loan_amount": 120030,
    "interest_rate": 8.12,
    "tenure": 12
}
``` | Create a new loan application |
| `api/view-loan/<int:loan_id>/` | `GET` | No request body needed | View specific loan details |
| `api/view-loans/<int:customer_id>/` | `GET` | No request body needed | View all loans for a customer |

## Automatic Data Seeding

This project features a "self-healing" data seeding mechanism. On startup, the Celery worker uses a `worker_ready` signal to check if the database is empty.

-   **If the database is empty:** It automatically dispatches a background task (`ingest_initial_data`) to read `customers.xlsx` and `loans.xlsx` from the root directory and populate the database using a highly efficient `bulk_create` operation.
-   **If data already exists:** The worker detects that the database is populated and skips the ingestion task.

This ensures that you always have your initial dataset ready without needing to run any manual commands after the first startup. To reset the database, you can run `docker-compose down --volumes` and then `docker-compose up`.
