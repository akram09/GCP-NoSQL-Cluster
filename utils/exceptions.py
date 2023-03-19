# This file includes the definition of the set of exceptions that are used in the code. The exceptions are defined in a class that inherits from the Exception class. 

class InvalidJsonException(Exception):
    pass


class InternalException(Exception):
    def __init__(self, message=None):
        if message:
            self.message = message
        else:
            self.message = "An internal error occurred."


class GCPSecretNotFoundException(InternalException):
    pass


class GCPStorageBucketCreationFailedException(InternalException):
    pass

class GCPUnsupportedOSFamilyException(InternalException):            
    pass

class GCPSecretCreationFailedException(InternalException):
    pass

class GCPSecretVersionCreationFailedException(InternalException):
    pass

class GCPKMSKeyCreationFailedException(InternalException):
    pass

class GCPKMSKeyPermissionAssignmentFailedException(InternalException):
    pass

class GCPKMSKeyRingCreationFailedException(InternalException):
    pass
    
class GCPInstanceSerialOutputException(InternalException):
    pass

class GCPImageNotFoundException(InternalException):
    pass

class GCPOperationFailedException(InternalException): 
    pass


class UnAuthorizedException(Exception):
    pass
