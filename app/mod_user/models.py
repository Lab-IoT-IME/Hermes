from app import db, ma
from app.mod_common.models import Base, BaseSimple


# Attributes
protectedFields = {'password', 'creationDate', 'lastUpdate'}


# Models definition
class User(Base):
  __tablename__ = 'Users'

  name          = db.Column(db.String(100), nullable=False)
  birthday      = db.Column(db.DateTime, nullable=False)
  email         = db.Column(db.String(50), nullable=False, unique=True)
  phone         = db.Column(db.String(20), nullable=False)
  password      = db.Column(db.String(100), nullable=False)

  typeId        = db.Column(db.Integer, db.ForeignKey('UserTypes.id'), nullable=False)
  userType      = db.relationship('UserType', uselist=False)

  userSensorsId = db.Column(db.Integer, db.ForeignKey('UserSensors.id'), nullable=False)
  userSensor    = db.relationship(
                    'UserSensors', uselist=False, 
                    single_parent=True, 
                    cascade="all, delete, delete-orphan"
                  )

  def __init__(self, name, birthday, email, phone, password, typeId):
    self.name = name
    self.birthday = birthday
    self.email = email
    self.phone = phone
    self.password = password
    self.typeId = typeId

    try:
      sensors = UserSensors(True, False)
      db.session.add(sensors)
      db.session.flush()
      self.userSensorsId = sensors.id
    except:
      print('Could not create User Sensors object')
      raise

  def __repr__(self): 
    return f"{self.id} - Name: {self.name}"

class UserSensors(BaseSimple):
  __tablename__ = 'UserSensors'

  HR = db.Column(db.Boolean, nullable=False, default=False)
  SpO2 = db.Column(db.Boolean, nullable=False, default=False)

  def __init__(self, HR, SpO2):
    self.HR = HR
    self.SpO2 = SpO2
  
  def __repr__(self):
    return f'{self.id} - HR: {self.HR} | SpO2: {self.SpO2}'

class UserType(BaseSimple):
  __tablename__ = 'UserTypes'

  name = db.Column(db.String(100), nullable=False)
  individual = db.Column(db.Boolean, nullable=False, default=False)

  def __init__(self, name, individual):
    self.name = name
    self.individual = individual
  
  def __repr__(self):
    return f"{self.id} - Name: {self.name} | Individual: {self.individual}"


# Schemas definition
class UserSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = User
  
  userSensor = ma.Nested("UserSensorsSchema")
  userType = ma.Nested("UserTypeSchema")

class UserSensorsSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = UserSensors

class UserTypeSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = UserType