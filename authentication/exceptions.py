class AppError(Exception):
    def __init__(self, message: str = None):
        self.message = message

    def __str__(self):
        return self.message


class ValidationError(AppError):
    pass


class EnvironmentValueError(AppError):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f"Error loading environmental variable: {self.key}"
