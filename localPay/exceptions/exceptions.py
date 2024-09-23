# exceptions.py

from fastapi import HTTPException


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

# User related exceptions
class UserNotFoundException(CustomException):
    def __init__(self, user_id: int):
        super().__init__(status_code=404, detail=f"User with id {user_id} not found")

class UserLoginNotFoundException(CustomException):
    def __init__(self, login: str):
        super().__init__(status_code=404, detail=f"User with login {login} not found")

class UserAlreadyExistsException(CustomException):
    def __init__(self, login: str):
        super().__init__(status_code=400, detail=f"User with login {login} already exists")

class InvalidUserDataException(CustomException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Invalid user data: {detail}")

# Payment related exceptions
class PaymentNotFoundException(CustomException):
    def __init__(self, payment_id: int):
        super().__init__(status_code=404, detail=f"Payment with id {payment_id} not found")

class InvalidPaymentDataException(CustomException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Invalid payment data: {detail}")

class PaymentCreationFailedException(CustomException):
    def __init__(self):
        super().__init__(status_code=500, detail="Failed to create payment")

class PaymentUpdateFailedException(CustomException):
    def __init__(self, payment_id: int):
        super().__init__(status_code=500, detail=f"Failed to update payment with id {payment_id}")

# Financial exceptions
class InsufficientFundsException(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=400, detail=f"Insufficient funds for this operation. Details: {detail}")

class InvalidAmountException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid amount specified")

class RefillExceedsLimitException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, detail="Refill amount exceeds allowed limit")

class WriteOffExceedsBalanceException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, detail="Write-off amount exceeds available balance")

# Authentication and Authorization exceptions
class UnauthorizedException(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=401, detail=f"Unauthorized. Details: {detail}")

class ForbiddenException(CustomException):
    def __init__(self, detail: str = None):
        super().__init__(status_code=403, detail=f"Forbidden. Details: {detail}")

class InvalidTokenException(CustomException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")

class TokenExpiredException(CustomException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token has expired")

class InvalidOrExpiredTokenException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid or expired token")

# Date and time related exceptions
class InvalidDateRangeException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid date range")

class InvalidDateFormatException(CustomException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Invalid date format. Details: {detail}")

# Database related exceptions
class DatabaseConnectionException(CustomException):
    def __init__(self):
        super().__init__(status_code=500, detail="Unable to connect to database")

class DatabaseQueryException(CustomException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Database query error: {detail}")

# File and export related exceptions
class FileExportFailedException(CustomException):
    def __init__(self, details: str):
        super().__init__(status_code=500, detail=f"Failed to export file. Details: {details}")

class InvalidFileFormatException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid file format")

# Region related exceptions
class InvalidRegionException(CustomException):
    def __init__(self, region: str):
        super().__init__(status_code=400, detail=f"Invalid region: {region}")

# Pagination related exceptions
class InvalidPaginationParametersException(CustomException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid pagination parameters")

# External service related exceptions
class ExternalServiceUnavailableException(CustomException):
    def __init__(self, service_name: str):
        super().__init__(status_code=503, detail=f"External service unavailable: {service_name}")

# Comment related exceptions
class CommentNotFoundException(CustomException):
    def __init__(self, comment_id: int):
        super().__init__(status_code=404, detail=f"Comment with id {comment_id} not found")

class InvalidCommentDataException(CustomException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Invalid comment data: {detail}")

# General exceptions
class ValidationException(CustomException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Validation error: {detail}")

class ResourceNotFoundException(CustomException):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(status_code=404, detail=f"{resource_type} with id {resource_id} not found")

class InternalServerErrorException(CustomException):
    def __init__(self):
        super().__init__(status_code=500, detail="Internal server error")
