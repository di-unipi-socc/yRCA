class Event: 
    def __init__(self,serviceName,serviceInstanceId,timestamp,message,severity):
        self.serviceName = serviceName
        self.instanceId = serviceInstanceId
        self.timestamp = timestamp
        self.message = message
        self.severity = severity