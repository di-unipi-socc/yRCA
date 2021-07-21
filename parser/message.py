from enum import Enum

class MessageType(Enum):
    CLIENT_SEND = 1
    CLIENT_RECEIVE = 2
    SERVER_RECEIVE = 3
    SERVER_SEND = 4
    OTHER = 5

class Parameters: 
    def __init__(self,service,requestId):
        self.service=service
        self.requestId=requestId

class Message:
    def __init__(self,type,parameters):
        if type not in list(MessageType):
            raise ValueError("Unknown message type")
        self.type=type
        self.parameters=parameters
    
    def print(self):
        if self.type == MessageType.CLIENT_SEND:
            print("ClientSend: ", self.parameters.service, self.parameters.requestId)
        elif self.type == MessageType.CLIENT_RECEIVE:
            print("ClientReceive: ", self.parameters.service, self.parameters.requestId)
        elif self.type == MessageType.SERVER_RECEIVE:
            print("ServerReceive: ", self.parameters.requestId)
        elif self.type == MessageType.SERVER_SEND:
            print("ServerSend: ", self.parameters.requestId)
        else:
            print("Other")