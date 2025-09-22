from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from django.db import IntegrityError, DatabaseError
from rest_framework.response import Response
from rest_framework import status


def main_exception_handler(exc, context):

        # it handle DRF standare exceptions first
    response = exception_handler(exc, context)

    # If it's a standard DRF-handled exception, return that response.
    if response is not None:
        return response

    # value errro handling
    if isinstance(exc, ValueError):
        custom_response_data = {
                'status': 'error',
                'details': str(exc) 
        }
     
        return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # validation error handling
    if isinstance(exc, ValidationError):
        custom_response_data = {
                'status': 'error',
                'details': str(exc)  
        }
     
        return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Assertion Error Handling 
    if isinstance(exc, AssertionError):
        error_message = str(exc)
        return Response(
                {"error": error_message or "Error In Response"}, 
                status=status.HTTP_409_CONFLICT
        )
    
    # Integrity Error Handling
    if isinstance(exc, IntegrityError):
        error_message = str(exc)
        return Response(
                {"error": error_message or "A user with these details already exists."}, 
                status=status.HTTP_409_CONFLICT
        )
        
        # Database Error Handling
    if isinstance(exc, DatabaseError):
        error_message = str(exc)
        return Response(
                {"error": str(error_message) or "A database error occurred. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
            
        # For any other exceptions, return a generic error response.
    return Response(
            {"error": str(exc) or "An unexpected error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

        # other error handling can be extendable from here

