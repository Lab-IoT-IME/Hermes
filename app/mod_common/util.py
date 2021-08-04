import argparse
from flask import jsonify
from app import app

def str2bool(v):
  if isinstance(v, bool):
    return v
  if v.lower() in ('yes', 'true', 't', 'y', '1'):
    return True
  elif v.lower() in ('no', 'false', 'f', 'n', '0'):
    return False
  else:
    raise argparse.ArgumentTypeError('Boolean value expected.')

def defaultError():
  with app.app_context():
    jsonify({'data': 'Could not retrieve data', 'success': False}), 400