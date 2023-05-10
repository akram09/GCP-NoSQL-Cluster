# Description: Utility functions that are used in the application.
from functools import wraps
from flask import request
from utils.exceptions import UnAuthorizedException, InternalException
from loguru import logger
from api.models.user import User
from api.extensions import couchbase



# create a decorator function that check first if the token has been passed in the headers, then check if the token is valid by interacting with the database on the user model, and then check if the user has the role admin 
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # get headers from request 
        headers = request.headers
        # check if the token has been passed in the headers
        if 'Authorization' not in headers:
            return {
                "error": "Unauthorized request. Please provide a valid token in the headers"
            }, 401
        # get the token
        token = headers['Authorization']
        # check if the token is valid
        try:
            user = check_token(token)
        except Exception as e:
            logger.error(f"Error checking token: {e}")
            return {
                "error": e.message
            }, 401
        # check if the user has the role admin
        if user.role != 'admin':
            return {
                "error": "Unauthorized request. You don't have the role admin"
            }, 401
        return f(*args, **kwargs)
    return decorated_function

# create the check_token function that check if the token is valid by interacting with the database on the user model
def check_token(token):
    # decode the token
    user = User.decode_auth_token(token)
    if not user:
        raise UnAuthorizedException("Invalid token")
    role = user['role']
    user_id = user['id']
    # get the user from the database
    if not couchbase.check("users", user_id):
        raise UnAuthorizedException("Invalid token")
    user_dict = couchbase.get("users", user_id)
    user = User.from_dict(user_dict)
    return user

