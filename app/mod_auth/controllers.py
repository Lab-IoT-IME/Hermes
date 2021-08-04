from flask import Blueprint, jsonify, request, Response
from app.mod_common.controllers import getUserByEmail
from config import SECRET_KEY
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from functools import wraps

modAuth = Blueprint('auth', __name__, url_prefix='/auth')

@modAuth.route('/', methods=['POST'])
def auth():
  auth = request.authorization
  print(auth)
  if not auth or not auth.username or not auth.password:
    return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"', 'success': False}), 401
  
  try:
    (user, userJson) = getUserByEmail(auth.username)
  except:
    user = None

  if not user:
    return jsonify({'message': 'User not found', 'success': False}), 401
  
  if check_password_hash(user.password, auth.password):
    (token, refresh, exp) = generateTokens(user.email)

    return jsonify({'message': 'Validated successfully', 'token': token, 'refresh': refresh,'exp': exp, 'user': userJson})
  
  return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"', 'success': False}), 401

@modAuth.route('/refresh', methods=['POST'])
def refresh():
  refToken = request.json.get('token')
  
  if not refToken:
    return jsonify({'message': 'refresh token is missing', 'success': False}), 401
  try:
    data = jwt.decode(refToken, SECRET_KEY, algorithms=["HS256"])
    (user, userJson) = getUserByEmail(data['email'])
  except Exception as e:
    print(e)
    return jsonify({'message': 'token is invalid or expired', 'success': False}), 401
  
  (newToken, newRefToken, newExp) = generateTokens(user.email)
  return jsonify({'message': 'Validated successfully', 'token': newToken, 'refresh': newRefToken,'exp': newExp, 'user': userJson})
  
def generateTokens(email):
  data = {
    'email': email, 
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
  }
  rData = {
    'email': email,
    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
  }
  token = jwt.encode(data, SECRET_KEY)
  refresh = jwt.encode(rData, SECRET_KEY)
  return (token, refresh, data['exp'])

def token_required(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    token = request.headers.get('Token')
    if not token:
      return jsonify({'message': 'token is missing', 'success': False}), 401
    try:
      data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
      current_user = getUserByEmail(data['email'])[0]
    except Exception as e:
      print(e)
      return jsonify({'message': 'token is invalid or expired', 'success': False}), 401
    return f(current_user, *args, **kwargs)
  return decorated

def admin_access(f):
  @token_required
  @wraps(f)
  def decorated(user, *args, **kwargs):
    if(user.typeId != 0):
      return jsonify({'message': 'admin restrict endpoint', 'success': False}), 401
    return f(*args, **kwargs)
  return decorated

def user_access(f):
  @token_required
  @wraps(f)
  def decorator(user, *args, **kwargs):
    if(user.typeId != 1 and kwargs['userId'] != user.id):
      return jsonify({'message': 'user restrict endpoint', 'success': False}), 401
    return f(*args, **kwargs)
  return decorator

def any_user_access(f):
  @token_required
  @wraps(f)
  def decorator(user, *args, **kwargs):
    return f(*args, **kwargs)
  return decorator