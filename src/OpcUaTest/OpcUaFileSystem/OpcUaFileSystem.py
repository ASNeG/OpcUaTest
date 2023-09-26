from opcua import ua

from OpcUaTest.Util import Log
from OpcUaTest.Util import Object

from OpcUaTest.OpcUaService import OpcUaSessionService


fileSystenInfo = Object.Object({
    "Property": {
        "AddMissingItem": True
    }
})


def open(inputParams, outputParams):
    # Check session name parameter
    if "SessionName" not in inputParams:
        inputParams["SessionName"] = "DefaultSession"
    
    # Check file system name
    if "FileSystemName" not in inputParams:
        inputParams["FileSystemName"] = "FileSystem1"
        
    # Check file system path
    if "FileSystemPath" not in inputParams:
        inputParams["FileSystemPath"] = "FileSystem1"
        
    # Get session from opc ua session service
    ip = {
        "SessionName": inputParams["SessionName"]
    }
    op = {}
    OpcUaSessionService.get(ip, op)
    if op["ResultCode"] != "OK":
        outputParams["ResultCode"] = "SessionInvalid"
        Log.error("OpcUaFileSystem:open", 1, "session not exist", inputParams)
        return
    client = op["Session"]
        
    # Check if file system already exist
    if fileSystenInfo.exist("FileSystemList." + inputParams["FileSystemName"]):
        outputParams["ResultCode"] = "OK"
        return
        
    # Find file system root node
    fileSystemNode = _findFileSystemNode(client.get_objects_node(), inputParams["FileSystemPath"])
    if fileSystemNode == None:
        outputParams["ResultCode"] = "PathInvalid"
        Log.error("OpcUaFileSystem:open", 3, "file system path invalid", inputParams)
        return
        
    # Add info element
    fileSystenInfo.FileSystemList[inputParams["FileSystemName"]] = {
        "FileSystemPath": inputParams["FileSystemPath"],
        "FileSystemNode": fileSystemNode,
        "Client": client
    }

    outputParams["ResultCode"] = "OK"
    
    
def close(inputParams, outputParams):    
    # Check file system name
    if "FileSystemName" not in inputParams:
        inputParams["FileSystemName"] = "FileSystem1"
        
    # Check if file system  already exist
    if not fileSystenInfo.exist("FileSystemList." + inputParams["FileSystemName"]):
        outputParams["ResultCode"] = "OK"
        return
        
    # Delete file system
    del fileSystenInfo.FileSystemList[inputParams["FileSystemName"]]
    
    outputParams["ResultCode"] = "OK"
    
    
def getNodeId(inputParams, outputParams):
    # Check filename
    if "FileName" not in inputParams:
        outputParams["ResultCode"] = "InvalidArgument"
        Log.error("createFile:getNodeId", 1, "FileName parameter not exist", inputParams)
        return
   
    # Check file system name
    if "FileSystemName" not in inputParams:
        inputParams["FileSystemName"] = "FileSystem1"
        
    # Check if file system is already exist
    if not fileSystenInfo.exist("FileSystemList." + inputParams["FileSystemName"]):
        outputParams["ResultCode"] = "InvalidArgument"
        Log.error("OpcUaFileSystem:getNodeId", 2, "file system not exist", inputParams)
        return
    fileSystemInfo = fileSystenInfo.FileSystemList[inputParams["FileSystemName"]];
    
    # Check if path already exist
    fileNode = _findFileSystemNode(fileSystemInfo.FileSystemNode, inputParams["FileName"])
    if fileNode == None:
        outputParams["ResultCode"] = "NotExist"
        return

    outputParams["Node"] = fileNode    
    outputParams["NodeId"] = fileNode.nodeid
    outputParams["ResultCode"] = "OK"
    
    
def deleteFile(inputParams, outputParams):
    # Check filename
    if "FileName" not in inputParams:
        outputParams["ResultCode"] = "InvalidArgument"
        Log.error("createFile:deleteFile", 1, "FileName parameter not exist", inputParams)
        return
   
    # Check file system name
    if "FileSystemName" not in inputParams:
        inputParams["FileSystemName"] = "FileSystem1"
        
    # Check if file system is already exist
    if not fileSystenInfo.exist("FileSystemList." + inputParams["FileSystemName"]):
        outputParams["ResultCode"] = "InvalidArgument"
        Log.error("OpcUaFileSystem:deleteFile", 2, "file system not exist", inputParams)
        return
    fileSystemInfo = fileSystenInfo.FileSystemList[inputParams["FileSystemName"]];
    
    # Check if path already exist
    fileNode = _findFileSystemNode(fileSystemInfo.FileSystemNode, inputParams["FileName"])
    if fileNode == None:
        outputParams["ResultCode"] = "OK"
        return
    
    # Get create file node
    deleteFileName = inputParams["FileName"].split('.')[:-1]
    deleteFileName.append("Delete")
    deleteFileName = ".".join(deleteFileName)
    deleteFileNode = _findFileSystemNode(fileSystemInfo.FileSystemNode, deleteFileName)
    if deleteFileNode == None:
        outputParams["ResultCode"] = "PathError"
        Log.error("OpcUaFileSystem:deleteFile", 3, "create file method not found in file system", 
            inputParams |
            {
                "FileSystemNode": fileSystemInfo.FileSystemNode,
                "DeleteFileName": deleteFileName
            }
        )
        return
    
    # Call delete file method
    parentNode = deleteFileNode.get_parent();
    res = parentNode.call_method(
        deleteFileNode.nodeid,
        ua.Variant(fileNode.nodeid, ua.VariantType.NodeId)
    )
    if res != None:
        outputParams["ResultCode"] = "CallMethodError"
        Log.error("OpcUaFileSystem:deleteFile", 5, "call method error", inputParams)
        return
    
    outputParams["ResultCode"] = "OK"
    
    
def createFile(inputParams, outputParams):
    # Check filename
    if "FileName" not in inputParams:
        outputParams["ResultCode"] = "InvalidArgument"
        Log.error("OpcUaFileSystem:createFile", 1, "FileName parameter not exist", inputParams)
        return
    
    # Check requested file open
    if "RequestedFileOpen" not in inputParams:
        inputParams["RequestedFileOpen"] = False;
    
    # Check file system name
    if "FileSystemName" not in inputParams:
        inputParams["FileSystemName"] = "FileSystem1"
        
    # Check if file system is already exist
    if not fileSystenInfo.exist("FileSystemList." + inputParams["FileSystemName"]):
        outputParams["ResultCode"] = "InvalidArgument"
        Log.error("OpcUaFileSystem:createFile", 2, "file system not exist", inputParams)
        return
    fileSystemInfo = fileSystenInfo.FileSystemList[inputParams["FileSystemName"]];
        
    # Check if path already exist
    fileNode = _findFileSystemNode(fileSystemInfo.FileSystemNode, inputParams["FileName"])
    if fileNode != None:
        outputParams["ResultCode"] = "Exist"
        Log.error("OpcUaFileSystem:createFile", 3, "file already exist in file system", inputParams)
        return
    
    # Get create file node
    createFileName = inputParams["FileName"].split('.')[:-1]
    createFileName.append("CreateFile")
    createFileName = ".".join(createFileName)
    createFileNode = _findFileSystemNode(fileSystemInfo.FileSystemNode, createFileName)
    if createFileNode == None:
        outputParams["ResultCode"] = "PathError"
        Log.error("OpcUaFileSystem:createFile", 4, "create file method not found in file system", 
            inputParams |
            {
                "FileSystemNode": fileSystemInfo.FileSystemNode,
                "CreateFileName": createFileName
            }
        )
        return
    
    # Call create file method
    parentNode = createFileNode.get_parent();
    res = parentNode.call_method(
        createFileNode.nodeid,
        ua.Variant(inputParams["FileName"].split('.').pop(), ua.VariantType.String),
        ua.Variant(inputParams["RequestedFileOpen"], ua.VariantType.Boolean)
    )
    if len(res) != 2:
        outputParams["ResultCode"] = "CallMethodError"
        Log.error("OpcUaFileSystem:createFile", 5, "call method error", inputParams)
        return
    
    outputParams["NodeId"] = res[0]
    outputParams["FileHandle"] = res[1]
    outputParams["ResultCode"] = "OK"
    
    
def openFile(inputParams, outputParams):
    pass


def closeFile(inputParams, outputParams):
    pass


def readFile(inputParams, outputParams):
    pass


def writeFile(inputParams, outputParams):
    pass

    
def _findFileSystemNode(startNode, path):
    # Check path
    if type(path).__name__ == "str":
        return _findFileSystemNode(startNode, path.split('.'))
    if type(path).__name__ != "list":
        return None
    
    if len(path) == 1:
        for actNode in startNode.get_children():
            if actNode.get_display_name().Text == path[0]: return actNode
    else:
        key = path.pop(0)
        for actNode in startNode.get_children():
            if actNode.get_display_name().Text == key: return _findFileSystemNode(actNode, path)
    
    return None


