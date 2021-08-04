from app import db

class BaseSimple(db.Model):
  __abstract__ = True

  id = db.Column(db.Integer, primary_key=True)

class Base(db.Model):
  __abstract__ = True

  id            = db.Column(db.Integer, primary_key=True)
  creationDate  = db.Column(db.DateTime, default=db.func.current_timestamp())
  lastUpdate    = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                         onupdate=db.func.current_timestamp())
