
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
    #print("Coommand is: " + str(command) + " id is " + str(task_id))
    filter = { '_id': task_id }
    try:
      command_execution = subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      #print("Process stdout: " + str(command_execution.stdout))
      #print("Process stderr: " + str(command_execution.stderr))
      saved_task = self.db.tasks.replace_one(filter, {'cmd': command, 'state': task_status.TaskStatus.FINISHED.value[0], 'output': command_execution.stdout})
    except:
      saved_task = self.db.tasks.replace_one(filter, {'cmd': command, 'state': task_status.TaskStatus.ERROR.value[0], 'output': ''})
