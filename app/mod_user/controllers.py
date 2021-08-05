from flask import Blueprint, jsonify, request
from app import db
from app.mod_user.models import User, UserSensors, UserSchema, UserSensorsSchema, UserType, UserTypeSchema, protectedFields
from werkzeug.security import generate_password_hash
from app.mod_common.util import str2bool
import datetime as dt
from app.mod_auth.controllers import admin_access, user_access

modUser = Blueprint('users', __name__, url_prefix='/users')

# Routes and methods calls
@modUser.route('/', methods=['GET'])
@admin_access
def users():
  # This method returns a list of users
  args = request.args.to_dict()
  return getUsers(args)
  
@modUser.route('/', methods=['POST'])
def newUser():
  # This method create a new user
  return createUser(request.json)

@modUser.route('/<int:userId>', methods=['GET', 'PATCH', 'DELETE'])
@user_access
def user(userId):
  # This method return a specific user
  if request.method == 'GET':
    return getUser(userId)

  # This method update a specific user
  if request.method == 'PATCH':
    return updateUser(userId, request.form)

  # This method delete a specific user 
  if request.method == 'DELETE':
    return deleteUser(userId)

@modUser.route('/<int:userId>/sensors', methods=['PATCH'])
@user_access
def userSensors(userId):
  return updateUserSensors(userId, request.form.to_dict())

@modUser.route('/types', methods=['GET'])
def usersTypes():
  # This method returns a list of users types
  args = request.args.to_dict()
  return getUsersTypes(args)

@modUser.route('/types', methods=['POST'])
@admin_access
def newUserType():
  # This method create a new user type
  return createUsersType(request.form.to_dict())

@modUser.route('/types/<int:typeId>', methods=['GET'])
def userType(typeId):
  # This method return a specific user type
  return getUserType(typeId)

@modUser.route('/types/<int:typeId>', methods=['PATCH', 'DELETE'])
@admin_access
def modifyUserType(typeId):  
  # This method update a specific user type
  if request.method == 'PATCH':
    return updateUserType(typeId, request.form)

  # This method delete a specific user type
  if request.method == 'DELETE':
    return deleteUserType(typeId)

# Methods definition
def getUsers(args):
  try:
    if len(args) == 0:
      users = User.query.all()
    else:
      users = User.query
      for key in args:
        search = f'%{args.get(key)}%'
        users = users.filter(getattr(User, key).like(search))
      users = users.all()
  except Exception as e:
    print(e)
    return jsonify({'data': 'Could not retrieve data', 'success': False}), 400
  
  user_schema = UserSchema(many=True)
  output = user_schema.dump(users)
  return jsonify({
    'data': output,
    'success': True
  })

def createUser(body):
  print(body)
  try:
    typeId = body['typeId'] if body['typeId'] != 0 else 1  
    user = User(
      body['name'], 
      dt.datetime.strptime(body['birthday'], '%Y-%m-%d'), 
      body['email'], 
      body['phone'], 
      generate_password_hash(body['password'], 'sha256'),
      typeId
    )
    db.session.add(user)
    db.session.commit()
  except Exception as e:
    print(e)
    return jsonify({'data': f'Could not create user! Check if the body is right.\n {str(e)}', 'success': False}), 400

  user_schema = UserSchema()
  output = user_schema.dump(user)
  return jsonify({
    'data': output,
    'success': True
  })

def getUser(userId):
  user = __tryGetUser__(userId)
  userSchema = UserSchema()
  
  if user is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404

  output = userSchema.dump(user)
  return jsonify({
    'data': output,
    'success': True
  })

def updateUser(userId, form):
  user = __tryGetUser__(userId)
  userSchema = UserSchema()

  if user is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404

  try:
    for key in form:
      if key in protectedFields:
        raise Exception
      setattr(user, key, form.get(key))
    db.session.commit()
  except:
    return jsonify({'data': 'Could not update data', 'success': False}), 400
  
  output = userSchema.dump(user)
  return jsonify({
    'data': output,
    'success': True
  })

def deleteUser(userId):
  user = __tryGetUser__(userId)

  if user is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404

  db.session.delete(user)
  db.session.commit()
  return jsonify({
    'data': 'User deleted',
    'success': True
  })

def updateUserSensors(userId, form):
  user = __tryGetUser__(userId)
  userSensorsSchema = UserSensorsSchema()

  if user is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404
  
  sensors = __tryGetUserSensors__(user)

  try:
    for key in form:
      if key in protectedFields:
        raise Exception
      setattr(sensors, key, str2bool(form.get(key)))
    db.session.commit()
  except Exception as e:
    return jsonify({'data': f'Could not update data. {str(e)}', 'success': False}), 400
  output = userSensorsSchema.dump(sensors)
  print(output)
  return jsonify({
    'data': output,
    'success': True
  })

def getUsersTypes(args):
  try:
    if len(args) == 0:
      types = UserType.query.all()
    else:
      types = UserType.query
      for key in args:
        search = f'%{args.get(key)}%'
        types = types.filter(getattr(UserType, key).like(search))
      types = types.all()
  except:
    return jsonify({'data': 'Could not retrieve data', 'success': False}), 400
  
  userType_schema = UserTypeSchema(many=True)
  output = userType_schema.dump(types)
  return jsonify({
    'data': output,
    'success': True
  })

def createUsersType(body):
  try:
    types = UserType(
      body['name'], 
      str2bool(body['individual'])
    )
    db.session.add(types)
    db.session.commit()
  except Exception as e:
    return jsonify({'data': f'Could not create user type! Check if the body is right.\n {str(e)}', 'success': False}), 400

  types = UserTypeSchema()
  output = user_type_schema.dump(types)
  return jsonify({
    'data': output,
    'success': True
  })

def getUserType(typeId):
  userType = __tryGetUserType__(typeId)
  userTypeSchema = UserTypeSchema()
  
  if userType is None:
    return jsonify({'data': 'User Type Not Found', 'success': False}), 404

  output = userTypeSchema.dump(userType)
  return jsonify({
    'data': output,
    'success': True
  })

def updateUserType(typeId, form):
  userType = __tryGetUserType__(typeId)
  userTypeSchema = UserTypeSchema()

  if userType is None:
    return jsonify({'data': 'User Type Not Found', 'success': False}), 404

  try:
    for key in form:
      if key in protectedFields:
        raise Exception
      setattr(userType, key, form.get(key))
    db.session.commit()
  except:
    return jsonify({'data': 'Could not update data', 'success': False}), 400
  
  output = userTypeSchema.dump(userType)
  return jsonify({
    'data': output,
    'success': True
  })

def deleteUserType(typeId):
  userType = __tryGetUserType__(typeId)

  if userType is None:
    return jsonify({'data': 'User Type Not Found', 'success': False}), 404

  db.session.delete(userType)
  db.session.commit()
  return jsonify({
    'data': 'User Type deleted',
    'success': True
  })

def __tryGetUser__(userId):
  user = User.query.filter_by(id=userId).first()
  return user

def __tryGetUserSensors__(user):
  sensors = UserSensors.query.filter_by(id=user.userSensor.id).first()
  return sensors

def __tryGetUserType__(typeId):
  user_type = UserType.query.filter_by(id=typeId).first()
  return user_type