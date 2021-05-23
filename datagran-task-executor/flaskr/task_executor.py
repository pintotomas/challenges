
import time
from . import task_status
import subprocess

class TaskExecutor:

  def __init__(self, db):
    self.db = db
    self._running = True
  
  def terminate(self):
    self._running = False

  def run(self, command, task_id):
    filter = { '_id': task_id }
    try:
      command_execution = subprocess.run(command.split(" "), stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
      saved_task = self.db.tasks.replace_one(filter, {'cmd': command,
                     'state': task_status.TaskStatus.FINISHED.value,
                     'output': command_execution.stdout + command_execution.stderr})
    except Exception as e:
      print("Exception occured while trying to execute command " + command + ". Error is: " + str(e))
      saved_task = self.db.tasks.replace_one(filter, 
                     {'cmd': command,
                      'state': task_status.TaskStatus.ERROR.value,
                      'output': ''})
