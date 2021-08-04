from app import db, ma
from app.mod_common.models import Base, BaseSimple
from app.mod_user.models import UserSchema

# Attributes
protectedFields = {}

#Models definition
class Device(Base):
  __tablename__ = 'Devices'

  mac           = db.Column(db.String(12), nullable=False)
  manufacturer  = db.Column(db.String(100), nullable=False)
  name          = db.Column(db.String(100), nullable=False)
  model         = db.Column(db.String(100), nullable=False)
  userId        = db.Column(db.Integer, nullable=False)

  typeId        = db.Column(db.Integer, db.ForeignKey('DeviceTypes.id'), nullable=False)
  deviceType    = db.relationship('DeviceType', uselist=False)

  def __init__(self, mac, manufacturer, name, model, typeId, userId):
    self.mac = mac
    self.manufacturer = manufacturer
    self.name = name
    self.model = model
    self.typeId = typeId
    self.userId = userId
  
  def __repr__(self):
    return f'{self.id} - Name: {self.name} | MAC: {self.mac}'
class DeviceType(BaseSimple):
  __tablename__ = 'DeviceTypes'

  name = db.Column(db.String(100), nullable=False)

  def __init__(self, name):
    self.name = name
  
  def __repr__(self):
    return f'{self.id} - {self.name}'

#Schemas definition
class DeviceSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Device

  deviceType  = ma.Nested('DeviceTypesSchema')
class DeviceTypesSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = DeviceType