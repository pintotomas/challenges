import os

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId
from . import task_status
import subprocess

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
        command = request.json['cmd']
        #TODO: Send to async queue before executing the command
        pending_status = task_status.TaskStatus.NOT_STARTED.value[0]
        error_status = task_status.TaskStatus.ERROR.value[0]
        try:
          command_execution = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          print("Process stdout: " + str(command_execution.stdout))
          print("Process stderr: " + str(command_execution.stderr))
          saved_task = db.tasks.insert_one({'cmd': command, 'state': pending_status, 'output': command_execution.stdout})
        except:
          saved_task = db.tasks.insert_one({'cmd': command, 'state': error_status, 'output': ''})
          
        return jsonify({"id" : str(saved_task.inserted_id)})

    @app.route("/get_output/<taskId>", methods = ['GET'])
    def find_one(taskId):
        task = db.tasks.find_one({"_id" : ObjectId(taskId)})
        task_output = task['output'].decode("utf-8")
        print(task)
        return jsonify({'output' : task_output, 'state': task['state'], 'cmd': task['cmd']})

    return app