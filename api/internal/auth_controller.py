from api.models.user import User
from api.extensions import couchbase
from utils.exceptions import UserAlreadyExistsException, UserDoesNotExistException, InvalidPasswordException


def register_user(user: User):
    """
    Controller function to register a new user and generate the jwt token for access. 
    """
    # insert user to the couchbase database
    user_dict = user.to_dict()
    # check if the user already exists 
    users = couchbase.list_filter("users", username=user_dict["username"])
    if len(list(users)) > 0:
        raise UserAlreadyExistsException("User already exists")
    couchbase.insert("users", user_dict["id"], user_dict)
    return user.encode_auth_token(user_dict["id"], user_dict["role"])

def login_user(username, password):
    """
    Controller function to login a user and generate the jwt token for access.
    """
    # check if the user exists 
    users = list(couchbase.list_filter("users", username=username))
    if len(users) == 0:
        raise UserDoesNotExistException("User does not exist")
    user_dict = users[0]["users"]
    user = User.from_dict(user_dict)
    # check if the password is correct
    if not user.check_password(user_dict["password"]):
        raise InvalidPasswordException("Incorrect password")
    # generate jwt token
    return user.encode_auth_token(user_dict["id"], user_dict["role"])


