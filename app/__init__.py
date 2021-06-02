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

from app.mod_user.controllers import modUser as userModule

app.register_blueprint(userModule)