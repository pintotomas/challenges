from enum import Enum

class ErrorCodes(Enum):
  TASK_NOT_FOUND = "TASK_NOT_FOUND",
  INVALID_ID = "INVALID_ID",
  INTERNAL_ERROR = "INTERNAL_ERROR"