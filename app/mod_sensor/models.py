from app import db, ma
from app.mod_common.models import BaseSimple


# Models definition
class Sensor(BaseSimple):
  __tablename__ = 'Sensors'

  deviceId = db.Column(db.Integer, nullable=False)
  model = db.Column(db.String(100), nullable=False)
  manufacturer = db.Column(db.String(100), nullable=False)

  typeId = db.Column(db.Integer, db.ForeignKey('SensorTypes.id'), nullable=False)
  sensorType = db.relationship('SensorType', uselist=False)

  def __init__(self, deviceId, model, manufacturer, typeId):
    self.deviceId = deviceId
    self.model = model
    self.manufacturer = manufacturer
    self.typeId = typeId
  
  def __repr__(self):
    return f'{self.id} - Model: {self.model}'

class SensorType(BaseSimple):
  __tablename__ = 'SensorTypes'

  name = db.Column(db.String(100))

  def __init__(self, name):
    self.name = name
  
  def __repr__(self):
    return f'{self.id} - Name: {self.name}'

class S_Base(BaseSimple):
  __abstract__ = True

  sensorId  = db.Column(db.Integer, nullable=True)
  userId    = db.Column(db.Integer, nullable=False)
  value     = db.Column(db.Float, nullable=False)
  date      = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
  setId     = db.Column(db.Integer, nullable=False)
  setSeq    = db.Column(db.Integer, nullable=False)

  def __init__(self, sensorId, userId, value, date, setId, setSeq):
    self.sensorId = sensorId
    self.userId = userId
    self.value = value
    self.date = date
    self.setId = setId
    self.setSeq = setSeq
  
  def __repr__(self):
    return f'{self.id} - Date: {self.date} | Value: {self.value}'

class S_HR(S_Base):
  __tablename__ = 'S-HR'

  def __init__(self, sensorId, userId, value, date, setId, setSeq):
    super().__init__(sensorId, userId, value, date, setId, setSeq)

class S_SpO2(S_Base):
  __tablename__ = 'S-SpO2'

  def __init__(self, sensorId, userId, value, date, setId, setSeq):
    super().__init__(sensorId, userId, value, date, setId, setSeq)


# Schemas definition
class SensorSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Sensor
  
  sensorType = ma.Nested('SensorTypeSchema')

class SensorTypeSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = SensorType

class S_HRSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = S_HR

class S_SpO2Schema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = S_SpO2


# Attributes
protectedFields = {}
sensorsMap = [
  ['HR', S_HR, S_HRSchema],
  ['SpO2', S_SpO2, S_SpO2Schema]
]