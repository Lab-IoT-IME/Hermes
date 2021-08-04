from flask import Blueprint, jsonify, request
from app import db
from app.mod_device.models import Device, DeviceType, DeviceSchema, DeviceTypesSchema, protectedFields
from app.mod_common.util import defaultError
from app.mod_auth.controllers import admin_access, user_access, any_user_access

modDevice = Blueprint('devices', __name__, url_prefix='/devices')

# Routes and methods calls
@modDevice.route('/', methods=['GET'])
@admin_access
def devices():
  # This method return a list of devices
  return getDevices(request.args)

@modDevice.route('/', methods=['POST'])
@any_user_access
def newDevice():
  # This method creates a new device
  return createDevice(request.form.to_dict())

@modDevice.route('/<int:userId>/<int:deviceId>', methods=['GET', 'PATCH', 'DELETE'])
@user_access
def device(deviceId):
  # This method return a specific device
  if request.method == 'GET':
    return getDevice(deviceId)
  
  # This method update a specific device
  if request.method == 'PATCH':
    return updateDevice(deviceId, request.form)

  # This method delete a specific device
  if request.method == 'DELETE':
    return deleteDevice(deviceId)

@modDevice.route('/types', methods=['GET', 'POST'])
@any_user_access
def deviceTypes():
  # This method return a list of devices types
  if request.method == 'GET':
    return getDeviceTypes(request.args)
  
  # This method creates a new device type
  if request.method == 'POST':
    return createDeviceType(request.form.to_dict())

@modDevice.route('/types/<int:typeId>', methods=['GET', 'PATCH', 'DELETE'])
@admin_access
def deviceType(typeId):
  # This method return a specific device type
  if request.method == 'GET':
    return getDeviceType(typeId)
  
  # This method update a specific device
  if request.method == 'PATCH':
    return updateDeviceType(typeId, request.form)

  # This method delete a specific device
  if request.method == 'DELETE':
    return deleteDeviceType(typeId)

# Methods definition
def getDevices(args):
  try:
    if len(args) == 0:
      devices = Device.query.all()
    else:
      devices = Device.query
      for key in args:
        search = f'%{args.get(key)}'
        devices = devices.filter(getattr(Device, key).like(search))
      devices = devices.all()
  except:
    return defaultError()
  
  device_schema = DeviceSchema(many=True)
  output = device_schema.dump(devices)
  return jsonify({
    'data': output,
    'success': True
  })

def createDevice(body):
  try:
    device = Device(
      body['mac'], 
      body['manufacturer'], 
      body['name'],
      body['model'],
      body['typeId'],
      body['userId']
    )
    db.session.add(device)
    db.session.commit()
  except Exception as e:
    return jsonify({'data': f'Could not create user! Check if the body is right.\n {str(e)}', 'success': False}), 400
  
  device_schema = DeviceSchema()
  output = device_schema.dump(device)
  return jsonify({
    'data': output,
    'success': True
  })

def getDevice(deviceId):
  device = __tryGetDevice__(deviceId)
  deviceSchema = DeviceSchema()

  if device is None:
    return jsonify({'data': 'Device Not Found', 'success': False}), 404
  
  output = deviceSchema.dump(device)
  return jsonify({
    'data': output,
    'success': True
  })

def updateDevice(deviceId, form):
  device = __tryGetDevice__(deviceId)
  deviceSchema = DeviceSchema()

  if device is None:
    return jsonify({'data': 'Device Not Found', 'success': False}), 404
  
  try:
    for key in form:
      if key in protectedFields:
        raise Exception
      setattr(device, key, form.get(key))
    db.session.commit()
  except Exception as e:
    print(e)
    return jsonify({'data': 'Could not update data', 'success': False}), 400
  
  output = deviceSchema.dump(device)
  return jsonify({
    'data': output,
    'success': True
  })

def deleteDevice(deviceId):
  device = __tryGetDevice__(deviceId)

  if device is None:
    return jsonify({'data': 'Device Not Found', 'success': False}), 404
  
  db.session.delete(device)
  db.session.commit()
  return jsonify({
    'data': 'User deleted',
    'success': True
  })

def getDeviceTypes(args):
  try:
    if len(args) == 0:
      deviceTypes = DeviceType.query.all()
    else:
      deviceTypes = DeviceType.query
      for key in args:
        search = f'%{args.get(key)}'
        deviceTypes = deviceTypes.filter(getattr(Device, key).like(search))
      deviceTypes = deviceTypes.all()
  except:
    return defaultError()
  
  deviceType_schema = DeviceTypesSchema(many=True)
  output = deviceType_schema.dump(deviceTypes)
  return jsonify({
    'data': output,
    'success': True
  })

def createDeviceType(body):
  try:
    deviceType = DeviceType(
      body['name']
    )
    db.session.add(deviceType)
    db.session.commit()
  except Exception as e:
    return jsonify({'data': f'Could not create device type! Check if the body is right.\n {str(e)}', 'success': False}), 400
  
  deviceType_schema = DeviceTypesSchema()
  output = deviceType_schema.dump(deviceType)
  return jsonify({
    'data': output,
    'success': True
  })

def getDeviceType(deviceId):
  deviceType = __tryGetDeviceType__(deviceId)
  deviceTypesSchema = DeviceTypesSchema()

  if deviceType is None:
    return jsonify({'data': 'Device Type Not Found', 'success': False}), 404
  
  output = deviceTypesSchema.dump(deviceType)
  return jsonify({
    'data': output,
    'success': True
  })

def updateDeviceType(typeId, form):
  deviceType = __tryGetDeviceType__(typeId)
  deviceTypesSchema = DeviceTypesSchema()

  if deviceType is None:
    return jsonify({'data': 'Device Type Not Found', 'success': False}), 404
  
  try:
    for key in form:
      if key in protectedFields:
        raise Exception
      setattr(deviceType, key, form.get(key))
    db.session.commit()
  except Exception as e:
    print(e)
    return jsonify({'data': 'Could not update data', 'success': False}), 400
  
  output = deviceTypesSchema.dump(deviceType)
  return jsonify({
    'data': output,
    'success': True
  })

def deleteDeviceType(typeId):
  deviceType = __tryGetDeviceType__(typeId)

  if deviceType is None:
    return jsonify({'data': 'Device type Not Found', 'success': False}), 404
  
  db.session.delete(deviceType)
  db.session.commit()
  return jsonify({
    'data': 'User Type deleted',
    'success': True
  })

def __tryGetDevice__(deviceId):
  device = Device.query.filter_by(id=deviceId).first()
  return device

def __tryGetDeviceType__(typeId):
  deviceType = DeviceType.query.filter_by(id=typeId).first()
  return deviceType