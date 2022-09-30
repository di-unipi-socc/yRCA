import sys,getopt

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

def lineConfig(line,service,invokeProb,failureProb,replicas):
    newLine = line.replace(service + "_INVOKE", str(invokeProb))
    newLine = newLine.replace(service + "_FAIL", str(failureProb))
    newLine = newLine.replace(service + "_REPLICAS", str(replicas))
    return newLine

def main(argv):
    # Parse command line arguments
    try:
        options,args = getopt.getopt(argv,"i:f:r:")
    except: 
        print("ERROR: Unsupported options were used")
        exit(-1)
    
    # Setting configuration values
    invokeProbability=75 # probability of invoking backend services
    failureProbability=10 # probability of failing in cascade
    replicas=1 # number of replicas
    for option, value in options: 
        if option in ["-i"]:
            invokeProbability = int(value)
            if invokeProbability<1 or failureProbability>100:
                print("ERROR: Invoke probability should be expressed as a percentage between 1 and 100")
                exit(-1)
        if option in ["-f"]:
            failureProbability = int(value)
            if failureProbability<1 or failureProbability>100:
                print("ERROR: Failure probability should be expressed as a percentage between 1 and 100")
                exit(-1)
        if option in ["-r"]:
            replicas = int(value)
            if replicas<1:
                print("ERROR: Cannot deploy less than 1 instance of application services")
                exit(-1)

    # Check input list of services to set for failure-prone behaviour
    if len(args)==0: 
        print("ERROR: Missing list of failing services")
        exit(-1)
    for s in args:
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
                l = lineConfig(l,s,invokeProbability,failureProbability,replicas)
            if s in l and s in healthyServices:
                l = lineConfig(l,s,invokeProbability,0,replicas)
        target.write(l)
    source.close()
    target.close()
    

if __name__ == "__main__":
    main(sys.argv[1:])