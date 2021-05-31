from flask import Blueprint
from app import db
from app.mod_user.models import User, UserSensors

mod_user = Blueprint('user', __name__, url_prefix='/user')

@mod_user.route('/get', methods=['GET'])
def get():
  users = User.query.all()
  for user in users:
    print(user.userType)

  return "ok", 200
