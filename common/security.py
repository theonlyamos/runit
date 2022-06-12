from flask import flash
from models import User
from common.utils import Utils


#def authenticate(password: str, user_password: str)-> bool:
#    return Utils.check_hashed_password(password, user_password)

def authenticate(email, password):
    user = User.get_by_email(email)
    if user:
        if Utils.check_hashed_password(password, user.password):
            return user
        flash("Invalid Login", 'danger')
    else:
        flash("User does not exist!", 'danger')
    return None


def identity(payload):
    user_id = payload['identity']
    return User.get(user_id)
