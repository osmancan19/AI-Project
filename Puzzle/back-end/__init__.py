from flask import Flask
from flask_cors import CORS

def create_app():
  app = Flask(__name__)
  CORS(app)

  from .views.puzzle import puzzle
  app.register_blueprint(puzzle)

  return app

# export FLASK_DEBUG=0
# export FLASK_APP=./