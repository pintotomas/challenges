import os

from flask import Flask, jsonify, request, make_response
from flask_apscheduler import APScheduler
from threading import Thread
from flask_pymongo import PyMongo
import bson
from . import task_executor, error_codes



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

    task_exec = task_executor.TaskExecutor(db)


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    @app.route("/new_task", methods = ['POST'])
    def add_one():
        command = request.json['cmd']
        try:
          saved_task = db.tasks.insert_one({'cmd': command, 'state': task_status.TaskStatus.NOT_STARTED.value})
          t = Thread(target = task_exec.run, args=(command, saved_task.inserted_id), daemon = True)
          t.start()
          return make_response({"id" : str(saved_task.inserted_id)}, 200)
        except Exception as e:
          return make_response(jsonify({"error": error_codes.ErrorCodes.INTERNAL_ERROR.value}), 500)


    @app.route("/get_output/<taskId>", methods = ['GET'])
    def find_one(taskId):
      try:
        task = db.tasks.find_one({"_id" : bson.ObjectId(taskId)})
        if not task:
          return make_response(jsonify({'error': error_codes.ErrorCodes.TASK_NOT_FOUND.value}))
        if not task['output']:
          return make_response(jsonify({'output' : '', 'state': task['state'], 
          'cmd': task['cmd']})
           , 200)
        task_output = task['output'].decode("utf-8")
        return make_response(jsonify({'output' : task_output, 'state': task['state'],
         'cmd': task['cmd']}), 200)
      except bson.errors.InvalidId:
        return make_response(jsonify({'error': error_codes.ErrorCodes.INVALID_ID.value}))
      

    return app