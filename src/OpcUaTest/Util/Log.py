from enum import IntEnum

from OpcUaTest.Util import Object

class LogLevel(IntEnum):
    ERROR = 0
    INFO = 1
    DEBUG = 2

    def logString(self):
        if self.value == LogLevel.ERROR:
            return "ERR"
        if self.value == LogLevel.INFO:
            return "INF"
        if self.value == LogLevel.DEBUG:
            return "DBG"

logConf = Object.Object({
    "LogLevel": LogLevel.INFO,
    "Cache": Object.Object({
        "isUsed": False,
        "messageStore": [],
        "hasErrors": False
    }),
    "Outputs": [print]
})

def messageOut(logCat, moduleId, msgId, message, inputParam):
    message = " ".join((logCat, moduleId, str(msgId), message, str(inputParam)))
    print(message)


def error(moduleId, msgId, message, inputParam):
    if logConf.LogLevel < LogLevel.ERROR:
        return
    messageOut(LogLevel.ERROR.logString(), moduleId, msgId, message, inputParam)


def info(moduleId, msgId, message, inputParam):
    if logConf.LogLevel < LogLevel.INFO:
        return
    messageOut(LogLevel.INFO.logString(), moduleId, msgId, message, inputParam)


def debug(moduleId, msgId, message, inputParam):
    if logConf.LogLevel < LogLevel.DEBUG:
        return
    messageOut(LogLevel.DEBUG.logString(), moduleId, msgId, message, inputParam)
