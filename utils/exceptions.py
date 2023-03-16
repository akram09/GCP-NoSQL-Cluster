# This file includes the definition of the set of exceptions that are used in the code. The exceptions are defined in a class that inherits from the Exception class. 

class InvalidJsonException(Exception):
    pass


class InternalException(Exception):
    pass


class GCPSecretNotFoundException(InternalException):
    description = "The supplied GCP secret was not found, and there was no default credentials supplied."
