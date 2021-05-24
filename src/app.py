from flask import Flask, jsonify, request, make_response
import pymongo
import task_executor
from enums.task_status import TaskStatus
from enums.error_codes import ErrorCodes
import bson
from threading import Thread
import os


app = Flask(__name__)

def get_db():
    client = pymongo.MongoClient(host='datagran_task_scheduler',
                         port=27017, 
                         username=os.environ['MONGO_INITDB_ROOT_USERNAME'], 
                         password=os.environ['MONGO_INITDB_ROOT_PASSWORD'],
                        authSource="admin")
    db = client[os.environ['MONGO_INITDB_DATABASE']]
    return db


# Saves a new task to the database with the state NOT_STARTED and starts a new thread 
# which executes the command.
#
# If the task is saved and the thread starts correctly, returns status 400 
#
# Returns status 400 if:
#   - 'cmd' is not found in the request json body
#
# Returns status 500 if there is any internal error  
# A command must be found in the request json body, otherwise a 500 Status is returned
# 
@app.route("/new_task", methods = ['POST'])
def add_one():
    try:
      command = request.json['cmd']
      db = get_db()
      task_exec = task_executor.TaskExecutor(db)

      saved_task = db.task_table.insert_one({'cmd': command, 'state': TaskStatus.NOT_STARTED.value})
      t = Thread(target = task_exec.run, args=(command, saved_task.inserted_id), daemon = True)
      t.start()
      return make_response({"id" : str(saved_task.inserted_id)}, 200)
    except KeyError as e:
      print("Key error: " + str(e))
      return make_response(jsonify({"error": ErrorCodes.COMMAND_MISSING.value}), 400)
    except Exception as e:
      print("Internal error while creating new task: " + str(e))
      return make_response(jsonify({"error": ErrorCodes.INTERNAL_ERROR.value}), 500)


# Returns a command and its status. The status can be:
#
# NOT_STARTED: The command wasn't executed
# STARTED: The command is currently being executed
# FINISHED_OK: The command could be executed correctly and without errors
# FINISHED_ERROR: The command could be executed, but it finished with errors
# NOT_EXECUTED: The command was not executed. (This could happen if the command doesn't exist)
#
# Also the output of the command is included in the response (can be empty depending on the status of the task)
#
# Returns status 400 if the taskId is not valid
#
# Returns status 404 if the taskId is valid but the command is not found
#
@app.route("/get_output/<taskId>", methods = ['GET'])
def find_one(taskId):
  try:
    db = get_db()

    task = db.task_table.find_one({"_id" : bson.ObjectId(taskId)})
    if not task:
      return make_response(jsonify({'error': ErrorCodes.TASK_NOT_FOUND.value}), 404)
    if 'output' not in task or not task['output']:
      return make_response(jsonify({'output' : '', 'state': task['state'], 
      'cmd': task['cmd']})
        , 200)
    task_output = task['output'].decode("utf-8")
    return make_response(jsonify({'output' : task_output, 'state': task['state'],
      'cmd': task['cmd']}), 200)
  except bson.errors.InvalidId:
    return make_response(jsonify({'error': ErrorCodes.INVALID_ID.value}), 400)
  


if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
