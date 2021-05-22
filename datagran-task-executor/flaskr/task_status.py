from enum import Enum

class TaskStatus(Enum):
  NOT_STARTED = "NOT_STARTED",
  STARTED = "STARTED",
  FINISHED = "FINISHED",
  ERROR = "ERROR"