# ---- Base Stage ----
FROM python:3.13-slim AS base


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# ---- Builder Stage ----
# This stage installs dependencies, including build tools
FROM base AS builder

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# ---- Final Stage ----
FROM base AS final


# Copy the installed Python packages from the builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Set the working directory
WORKDIR /app

# Copy the application code from your local machine to the container
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 8000

# The command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "credit_approver.wsgi:application"]
