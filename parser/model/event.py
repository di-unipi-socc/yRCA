# class for representing logged events
class Event: 
    def __init__(self,serviceName,serviceInstanceId,timestamp,message,severity):
        # name of the service whose instance is logging the event
        self.serviceName = serviceName.lower()
        # id of the service instance actually logging the event
        self.instanceId = serviceInstanceId.lower()
        # timestamp associated with the logged event
        self.timestamp = timestamp
        # message included in the logged event
        self.message = message
        # severity level of the logged event (as per the Syslog standard: https://datatracker.ietf.org/doc/html/rfc5424)
        self.severity = severity