from flask import Blueprint, jsonify, request
from app import db
from app.mod_sensor.models import Sensor, SensorType, S_HR, S_SpO2, SensorSchema, SensorTypeSchema, S_HRSchema, S_SpO2Schema, protectedFields, sensorsMap
from app.mod_common.util import str2bool
import datetime as dt
from app.mod_auth.controllers import admin_access, user_access, any_user_access

modSensor = Blueprint('sensors', __name__, url_prefix='/sensors')

# Routes and methods calls
@modSensor.route('/', methods=['GET'])
@admin_access
def allSensors():
  # This method returns a list of sensors
  if request.method == 'GET':
    args = request.args.to_dict()
    return getSensors(args)

@modSensor.route('/', methods=['POST'])
@any_user_access
def newSensor():
  # This method create a new sensor
  return createSensor(request.form.to_dict())

@modSensor.route('/<int:userId>/<int:sensorId>', methods=['GET', 'PATCH', 'DELETE'])
@user_access
def sensor(sensorId):
  # This method return a specific sensor
  if request.method == 'GET':
    return getSensor(sensorId)

  # This method update a specific sensor
  if request.method == 'PATCH':
    return updateSensor(sensorId, request.form)

  # This method delete a specific sensor  
  if request.method == 'DELETE':
    return deleteSensor(sensorId)

@modSensor.route('/<int:userId>/device/<int:deviceId>', methods=['GET'])
@user_access
def deviceSensors(deviceId):
  # This method returns a device sensors
  return getDeviceSensors(deviceId)

@modSensor.route('/<int:userId>/data', methods=['GET'])
@user_access
def sensorData(userId):
  # This method returns sensors data based on header parameters
  return getSensorsData(request.args)

@modSensor.route('/data', methods=['POST'])
@any_user_access
def newSensorData():
  # This method create sensors data based on body parameters
  return createSensorData(request.json)

@modSensor.route('/<int:userId>/data/<int:typeId>/<int:dataId>', methods=['PATCH', 'DELETE'])
@user_access
def alterSensorData(typeId, dataId):
  # This method update a specific sensor data
  if request.method == 'PATCH':
    return updateSensorData(typeId, dataId, request.form)

  # This mehtod delete a specific sensor data
  if request.method == 'DELETE':
    return deleteSensorData(typeId, dataId)

@modSensor.route('/types', methods=['GET'])
@any_user_access
def sensorsTypes():
  return getSensorsTypes(request.args)

@modSensor.route('/types/<int:typeId>', methods=['GET'])
@any_user_access
def sensorsType(typeId):
  return getSensorsType(typeId)

# Methods definition
def getSensors(args):
  try:
    if len(args) == 0:
      sensors = Sensor.query.all()
    else:
      sensors = Sensor.query
      for key in args:
        search = f'%{args.get(key)}%'
        sensors = sensors.filter(getattr(Sensor, key).like(search))
      sensors = sensors.all()
  except:
    return jsonify({'data': 'Could not retrieve data', 'success': False}), 400
  
  sensors_schema = SensorSchema(many=True)
  output = sensors_schema.dump(sensors)
  return jsonify({
    'data': output,
    'success': True
  })

def getSensor(sensorId):
  sensor = Sensor.query.filter_by(id=sensorId).first()
  sensorSchema = SensorSchema()
  
  if sensor is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404

  output = sensorSchema.dump(sensor)
  return jsonify({
    'data': output,
    'success': True
  })

def createSensor(body):
  try:
    sensor = Sensor(
      body['deviceId'], 
      body['model'], 
      body['manufacturer'], 
      body['typeId']
    )
    db.session.add(sensor)
    db.session.commit()
  except Exception as e:
    return jsonify({'data': f'Could not create user! Check if the body is right.\n {str(e)}', 'success': False}), 400
  
  sensor_schema = SensorSchema()
  output = sensor_schema.dump(sensor)
  return jsonify({
    'data': output,
    'success': True
  })

def updateSensor(sensorId, form):
  sensor = Sensor.query.filter_by(id=sensorId).first()
  sensorSchema = SensorSchema()

  if sensor is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404

  try:
    for key in form:
      if key in protectedFields:
        raise Exception
      setattr(sensor, key, form.get(key))
    db.session.commit()
  except Exception as e:
    print(e)
    return jsonify({'data': 'Could not update data', 'success': False}), 400
  
  output = sensorSchema.dump(sensor)
  return jsonify({
    'data': output,
    'success': True
  })

def deleteSensor(sensorId):
  sensor = Sensor.query.filter_by(id=sensorId).first()

  if sensor is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404
  
  # TODO: Handle error
  db.session.delete(sensor)
  db.session.commit()
  return jsonify({
    'data': 'User deleted',
    'success': True
  })

def getDeviceSensors(deviceId):
  sensors = Sensor.query.filter_by(deviceId=deviceId).all()

  if sensors is None:
    return jsonify({'data': 'User Not Found', 'success': False}), 404

  sensors_schema = SensorSchema(many=True)
  output = sensors_schema.dump(sensors)
  return jsonify({
    'data': output,
    'success': True
  })

def getSensorsData(args):
  params = args.to_dict()

  sensorTypes = ['0', '1']
  lastSet = False
  sensorsIds = []
  usersIds = []
  devicesIds = []
  dateInterval = [False, '1900-01-01', '9999-12-31']

  response = {}

  if('sensorTypes' in params):
    sensorTypes = params['sensorTypes'].split(',')
  
  if('lastSet' in params):
    lastSet = str2bool(params['lastSet'])
  
  if('sensorsIds' in params):
    sensorsIds = params['sensorsIds'].split(',')
  
  if('usersIds' in params):
    usersIds = params['usersIds'].split(',')
  
  if('initDate' in params):
    dateInterval[0] = True
    dateInterval[1] = params['initDate']
  
  if('endDate' in params):
    dateInterval[0] = True
    dateInterval[2] = params['endDate']

  for idx in sensorTypes:
    curSensor = sensorsMap[int(idx)]

    userSensorSet = {}
    response[curSensor[0]] = {}
    resp = response[curSensor[0]]

    data = curSensor[1].query.order_by(curSensor[1].setId.desc())

    if(len(usersIds) > 0):
      data = data.filter(curSensor[1].userId.in_(usersIds))

    if(len(sensorsIds) > 0):
      data = data.filter(curSensor[1].sensorId.in_(sensorsIds))

    if(dateInterval[0]):
      data = data.filter(curSensor[1].date.between(dateInterval[1], dateInterval[2]))

    if(lastSet):
      data.limit(100)
    
    data = data.all()

    for item in data:
      if(str(item.userId) not in resp):
        resp[str(item.userId)] = []

      if(lastSet and str(item.userId) in userSensorSet and item.setId < userSensorSet[str(item.userId)]):
        continue

      resp[str(item.userId)].append({
        'id': item.id,
        'sensorId': item.sensorId,
        'setId': item.setId,
        'setSeq': item.setSeq,
        'date': item.date,
        'value': item.value
      })
      userSensorSet[str(item.userId)] = item.setId

  return jsonify(response)

def createSensorData(body):
  print(body)
  if('typeId' not in body):
    return jsonify({'data': 'Could not create data! Check if the body is right.', 'success': False}), 400

  try:
    SensorData = sensorsMap[int(body['typeId'])][1]
    
    values = body['value'].split(',')
    initSeq = body['setSeq']
    sensorDataList = []

    if 'date' not in body:
      date = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
      date = dt.datetime.strptime(body['date'], '%Y-%m-%d %H:%M:%S')

    for value in values:
      sensorData = SensorData(
        body['sensorId'], 
        body['userId'], 
        value, 
        date,
        body['setId'],
        initSeq
      )
      sensorDataList.append(sensorData)
      db.session.add(sensorData)
      initSeq += 1

    db.session.commit()
  except Exception as e:
    print(e)
    return jsonify({'data': f'Could not create data! Check if the body is right.\n {str(e)}', 'success': False}), 400
  
  if(body.get('shortOut') == True):
    output = "ok"
  else:
    output = []
    sensorData_schema = sensorsMap[int(body['typeId'])][2]()
    for sData in sensorDataList:
      output = sensorData_schema.dump(sensorData)
  print(output)
  return jsonify({
    'data': output,
    'success': True
  })

def updateSensorData(typeId, dataId, form):
  if(int(typeId) >= len(sensorsMap)):
    return jsonify({'data': 'Could not update sensor data! Check if the body is right.', 'success': False}), 400

  try:
    SensorData = sensorsMap[int(typeId)][1]
    sensorData_schema = sensorsMap[int(typeId)][2]()

    sensorData = SensorData.query.filter_by(id=dataId).first()

    if sensorData is None:
      return jsonify({'data': 'UserData Not Found', 'success': False}), 404

    for key in form:
      if key in protectedFields:
        raise Exception
      setattr(sensorData, key, form.get(key))

    db.session.commit()
  except Exception as e:
    return jsonify({'data': 'Could not update data', 'success': False}), 400
    
  output = sensorData_schema.dump(sensorData)
  return jsonify({
    'data': output,
    'success': True
  })

def deleteSensorData(typeId, dataId):
  if(int(typeId) >= len(sensorsMap)):
    return jsonify({'data': 'Could not update sensor data! Check if the body is right.', 'success': False}), 400

  try:
    SensorData = sensorsMap[int(typeId)][1]

    sensorData = SensorData.query.filter_by(id=dataId).first()

    if sensorData is None:
      return jsonify({'data': 'UserData Not Found', 'success': False}), 404

    db.session.delete(sensorData)
    db.session.commit()
  except Exception as e:
    return jsonify({'data': 'Could not delete register', 'success': False}), 400

  return jsonify({
    'data': 'Data deleted',
    'success': True
  })

def getSensorsTypes(args):
  try:
    if len(args) == 0:
      sensorsTypes = SensorType.query.all()
    else:
      sensorsTypes = SensorType.query
      for key in args:
        search = f'%{args.get(key)}%'
        sensorsTypes = sensorsTypes.filter(getattr(SensorType, key).like(search))
      sensorsTypes = sensorsTypes.all()
  except:
    return jsonify({'data': 'Could not retrieve data', 'success': False}), 400
  
  sensorsTypes_schema = SensorTypeSchema(many=True)
  output = sensorsTypes_schema.dump(sensorsTypes)
  return jsonify({
    'data': output,
    'success': True
  })

def getSensorsType(typeId):
  sensorType = SensorType.query.filter_by(id=typeId).first()
  sensorTypeSchema = SensorTypeSchema()
  
  if sensorType is None:
    return jsonify({'data': 'Sensor Type Not Found', 'success': False}), 404

  output = sensorTypeSchema.dump(sensorType)
  return jsonify({
    'data': output,
    'success': True
  })
