import sys

# List of configurable Sock Echo services
services = [ 
    "FRONTEND",
    "ORDERS",
    "ORDERSDB",
    "CATALOGUE",
    "CATALOGUEDB",
    "USERS",
    "USERSDB",
    "CARTS",
    "CARTSDB",
    "PAYMENT",
    "SHIPPING",
    "RABBITMQ",
    "QUEUEMASTER"
]

def lineConfig(line,service,failureProbability):
    newLine = line.replace(service + "_INVOKE", "75")
    newLine = newLine.replace(service + "_FAIL", str(failureProbability))
    newLine = newLine.replace(service + "_REPLICAS", "2")
    return newLine

def main(argv):
    # Check input list of services to set for failure-prone behaviour
    if len(argv)==0: 
        print("ERROR: Missing list of failing services")
        exit(-1)
    for s in argv:
        if s.upper() not in services:
            print("ERROR: " + s + " is not a configurable service")
            exit(-1)
    
    # Failing vs non-failing services
    failingServices = []
    for s in argv:
        failingServices.append(s.upper())
    healthyServices = []
    for s in services:
        if s not in failingServices:
            healthyServices.append(s)     
    
    # Generate configured Docker Compose file
    source = open("docker-compose.yml","r")
    target = open("docker-compose-configured.yml","w")
    for l in list(source):
        for s in services:
            if s in l and s in failingServices:
                l = lineConfig(l,s,10)
            if s in l and s in healthyServices:
                l = lineConfig(l,s,0)
        target.write(l)
    source.close()
    target.close()
    

if __name__ == "__main__":
    main(sys.argv[1:])