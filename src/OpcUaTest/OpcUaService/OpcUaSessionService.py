from opcua import Client
from opcua.ua import UaError

from OpcUaTest.Util import Log
from OpcUaTest.Util import Object

sessionInfo = Object.Object({
    "Property": {
        "AddMissingItem": True
    }
})


def connect(inputParams, outputParams):
    
    # Check server url parameter
    if "ServerUrl" not in inputParams:
        outputParams["ResultCode"] = "InvalidArgument"
        Log.error("OpcUaSessionService:open", 1, "ServerUrl parameter not exist", inputParams)
        return
    
    # Check session name parameter
    if "SessionName" not in inputParams:
        inputParams["SessionName"] = "DefaultSession"
        
    # Check if session already exist
    if sessionInfo.exist("SessionList." + inputParams["SessionName"]):
        outputParams["ResultCode"] = "OK"
        return 
    
    # Create new session and connect to opc ua server
    try:
        client = Client(inputParams["ServerUrl"])
        client.connect()
    except UaError as e:
        outputParams["ResultCode"] = "ConnectError"
        outputParams["Error"] = str(e)
        Log.error("OpcUaSessionService:sessionOpen", 2, "connect to opc ua server failed", inputParams | outputParams)
        return
    sessionInfo.SessionList[inputParams["SessionName"]] = client
    
    outputParams["ResultCode"] = "OK"
    
    
def disconnect(inputParams, outputParams):
    # Check session name parameter
    if "SessionName" not in inputParams:
        inputParams["SessionName"] = "DefaultSession"
        
    # Check if session already exist
    if not sessionInfo.exist("SessionList." + inputParams["SessionName"]):
        outputParams["ResultCode"] = "OK"
        return
    
    # disconnect from opc ua server
    client = sessionInfo.SessionList[inputParams["SessionName"]]
    try:
        client.disconnect()                                        
    except UaError as e:
        outputParams["ResultCode"] = "DisconnectError"
        outputParams["Error"] = str(e)
        Log.error("OpcUaSessionService:disconnect", 1, "disconnect from opc ua server failed", inputParams | outputParams)
        return
    
    del sessionInfo.SessionList[inputParams["SessionName"]]
    
    outputParams["ResultCode"] = "OK"
    
    
    
def get(inputParams, outputParams):
    # Check session name parameter
    if "SessionName" not in inputParams:
        inputParams["SessionName"] = "DefaultSession"
        
    # Check if session already exist
    if not sessionInfo.SessionList.exist(inputParams["SessionName"]):
        outputParams["ResultCode"] = "NotExist"
        return
    
    outputParams["ResultCode"] = "OK"
    outputParams["Session"] = sessionInfo.SessionList[inputParams["SessionName"]]
    
    