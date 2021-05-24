from enums.task_status import TaskStatus
import subprocess

class TaskExecutor:

  def __init__(self, db):
    self.db = db

  # Runs a command and saves it status in the DB 
  # If the command is not valid, the task is not executed and it's updated to NOT_EXECUTED
  # status in the database.
  def run(self, command, task_id):
    filter = { '_id': task_id }
    try:
      self.db.task_table.replace_one(filter, {'cmd': command,
                     'state': TaskStatus.STARTED.value})
      command_execution = subprocess.run(command.split(" "), stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)
      if len(command_execution.stderr) > 0:
        execution_state =  TaskStatus.FINISHED_ERROR.value
      else: 
        execution_state =  TaskStatus.FINISHED_OK.value

      saved_task = self.db.task_table.replace_one(filter, {'cmd': command,
                     'state': execution_state,
                     'output': command_execution.stdout + command_execution.stderr})
    except Exception as e:
      print("Exception occured while trying to execute command " + command + ". Error is: " + str(e))
      saved_task = self.db.task_table.replace_one(filter, 
                     {'cmd': command,
                      'state': str(TaskStatus.NOT_EXECUTED.value)})
