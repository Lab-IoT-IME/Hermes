from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Credentials'] = 'true'
    header['Access-Control-Allow-Methods'] = 'GET,HEAD,OPTIONS,POST,PUT'
    header['Access-Control-Allow-Headers'] = '*'
    return response

from app.mod_auth.controllers import modAuth as authModule
from app.mod_user.controllers import modUser as userModule
from app.mod_device.controllers import modDevice as deviceModule
from app.mod_sensor.controllers import modSensor as sensorModule

app.register_blueprint(authModule)
app.register_blueprint(userModule)
app.register_blueprint(deviceModule)
app.register_blueprint(sensorModule)