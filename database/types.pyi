from enum import StrEnum
from typing import TypedDict, Optional


class MsgTypes(StrEnum):
    ERROR_REPORT = "ERROR_REPORT"
    TICKET = "TICKET"


class ExecStatus(StrEnum):
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"

class DbExecResult(TypedDict):
    status: ExecStatus
    message: Optional[str]
    error:  Optional[Exception]