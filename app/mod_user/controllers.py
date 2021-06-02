from flask import Blueprint, jsonify, request, Response
from app import db
from app.mod_user.models import User, UserSchema
import datetime as dt

modUser = Blueprint('users', __name__, url_prefix='/users')

@modUser.route('/', methods=['GET', 'POST'])
def users():
  # This method returns a list of users
  if request.method == "GET":
    try:
      users = User.query.all()
    except:
      return "Could not retrieve data"
    
    user_schema = UserSchema(many=True)
    output = user_schema.dump(users)
    return jsonify({
      'data': output,
      'response': "Data retrieved"
    })
  
  # This method create a new user
  if request.method == "POST":
    body = request.form.to_dict()
    try:
      user = User(body['name'], dt.datetime.strptime(body['birthday'], '%Y-%m-%d'), body['email'], body['phone'], body['password'], body['passSalt'], body['typeId'])
      # TODO: Implement method to save data to db
    except:
      return "Could not create user! Check if the body is right", 400

    user_schema = UserSchema()
    output = user_schema.dump(user)
    return jsonify({
      'data': output,
      'response': "User created"
    })

@modUser.route('/<int:userId>', methods=['GET'])
def user(userId):
  if request.method == "GET":
    user = User.query.filter_by(id=userId).first()
    if user is None:
      return "User Not Found", 404
    else:
      user_schema = UserSchema()
      output = user_schema.dump(user)
      return jsonify({
        'data': output,
        'response': "Data retrieved"
      })