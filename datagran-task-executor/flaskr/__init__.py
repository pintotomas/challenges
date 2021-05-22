import os

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from . import task_status

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config["MONGO_URI"] = "mongodb://admin:admin@localhost:27017/tasks?authSource=admin"
    mongodb_client = PyMongo(app)
    db = mongodb_client.db
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    @app.route("/new_task", methods = ['POST'])
    def add_one():
        pending_status = task_status.TaskStatus.NOT_STARTED.value[0]
        saved_task = db.tasks.insert_one({'cmd': request.json['cmd'], 'state': pending_status})
        return jsonify({"id" : str(saved_task.inserted_id)})

    return app