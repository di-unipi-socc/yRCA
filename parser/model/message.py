from enum import Enum

# class for distinguishing the "type" of events
# (currently distingushing "interaction events" from all "other events")
class MessageType(Enum):
    # CLIENT events
    CLIENT_SEND = 1
    CLIENT_RECEIVE = 2
    CLIENT_ERROR = 3
    CLIENT_TIMEOUT = 4
    # SERVER events
    SERVER_RECEIVE = 5
    SERVER_SEND = 6
    # OTHER events
    OTHER = 7

# class for specifying event-specific parameters
# (currently only used for "interactions")
class Parameters: 
    def __init__(self,service,requestId):
        self.service=service
        self.requestId=requestId

# class for representing messages in terms of the "type" of event they correspond to and of event specific "parameters"
class Message:
    def __init__(self,type,content,parameters):
        if type not in list(MessageType):
            raise ValueError("Unknown message type")
        # "MessageType" denoting the type of event corresponding to the message
        self.type=type
        # message content (plain text)
        self.content=content.replace("'","")
        # event-specific "Parameters"
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