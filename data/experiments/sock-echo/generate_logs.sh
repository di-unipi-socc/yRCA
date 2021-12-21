#!/bin/bash

deploy_and_load() {
    # input parameters
    requestPeriod=$1
    logName=$2
    results=$3

    # deploy "sock-echo"
    echo "* Docker deployment started" 
    touch echo-stack.log
    chmod ugo+rw echo-stack.log
    docker stack deploy -c docker-compose.yml sockecho
    echo "* Waiting for services to get online"
    sleep 300
    echo "* Docker deployment completed"

    # load "sock-echo" with given "rate"
    echo "* Generating workload"
    fault=0
    curlLog="curl.log"
    loglines=0
    while [ $fault -lt 100 ] && [ $loglines -le 1000000 ] # loop until at least 100 frontend failures happened
    do
        ./generate_workload.sh -d 180 -p $requestPeriod > $curlLog
        fault=$(grep ERROR echo-stack.log | grep _edgeRouter | grep -v own | wc -l)
        loglines=$(cat echo-stack.log | wc -l)
        echo "Generated faults: ${fault}"
    done
    rm $curlLog
    echo "* Waiting for logstash to collect all produced logs"
    sleep 60

    # undeploy "sock-echo"
    echo "* Undeployment started"
    docker stack rm sockecho
    echo "* Undeployment completed"

    # save logs
    mv echo-stack.log all-$logName.log
    mv *.log $results
    echo "* Log files stored in ${results}"

    # restore original docker file
    mv docker-compose.yml.original docker-compose.yml
    echo "* Original log file restored"

    # clean Docker environment and wait before next run
    echo "* Cleaning experiment's environment"
    docker container prune -f
    docker network prune -f
    systemctl restart docker
    sleep 30
} 

serviceList="edgeRouter frontend orders ordersDb catalogue catalogueDb users usersDb carts cartsDb payment shipping rabbitMq queueMaster"

# download load script from "chaos-echo"
#curl https://raw.githubusercontent.com/di-unipi-socc/chaos-echo/main/deploy/examples/sock-echo/logstash.conf --silent > logstash.conf
curl https://raw.githubusercontent.com/di-unipi-socc/chaos-echo/main/generate_workload.sh --silent > generate_workload.sh
chmod ugo+x generate_workload.sh

# *******************************************
# EXPERIMENT 1.1: Varying amount of logs, based on increasing end-user's load
# (shipping set to fail with probability 0.5, other services set to not fail on their own)
# (all services set to invoke backend services with probability 0.5)
# *******************************************

echo ""
echo "========================="
echo "     Experiment 1.1"
echo "========================="
    
# create folder where to store the logs
results="logs_exp11_loadRate"
mkdir $results

requestPeriods="0.1 0.04 0.02 0.01333 0.01"
failingService="shipping"
for requestPeriod in $requestPeriods; do 	
    echo "RATE: ${requestPeriod}^(-1)" 
    # generate docker-compose file with single point of failure 
    cp docker-compose.yml docker-compose.yml.original
    for service in $serviceList ; do
        # all services set to be replicated over 3 instances
        sed -i "s/${service^^}_REPLICAS/3/" docker-compose.yml
        # all services invoking backend services with probability 0.5
        sed -i "s/${service^^}_INVOKE/50/" docker-compose.yml
        # all services (but shipping) not failing on their own
        if [ $service != $failingService ]; then
            sed -i "s/${service^^}_FAIL/0/" docker-compose.yml
        # shipping failing with probability 0.5
        else 
            sed -i "s/${service^^}_FAIL/50/" docker-compose.yml
        fi 
    done
    echo "* Docker compose file generated"

    deploy_and_load $requestPeriod $requestPeriod $results 
done 

# *******************************************
# EXPERIMENT 1.2: Varying amount of logs, based on increasing invoke probability
# (shipping set to fail with probability 0.5, other services set to not fail on their own)
# (end-users' load set to send 10 requests/sec)
# *******************************************

echo ""
echo "========================="
echo "     Experiment 1.2"
echo "========================="
    
# create folder where to store the logs
results="logs_exp12_invokeProbability"
mkdir $results

invokeProbabilities="10 25 50 75 100"
failingService="shipping"
for invokeProbability in $invokeProbabilities; do 	
    echo "INVOKE PROBABILITY ${invokeProbability}" 
    # generate docker-compose file with single point of failure 
    cp docker-compose.yml docker-compose.yml.original
    for service in $serviceList ; do
        # all services set to be replicated over 3 instances
        sed -i "s/${service^^}_REPLICAS/3/" docker-compose.yml
        # all services invoking backend services with probability "invokeProbability"
        sed -i "s/${service^^}_INVOKE/${invokeProbability}/" docker-compose.yml
        # all services (but shipping) not failing on their own
        if [ $service != $failingService ]; then
            sed -i "s/${service^^}_FAIL/0/" docker-compose.yml
        # shipping failing with probability 0.5
        else 
            sed -i "s/${service^^}_FAIL/50/" docker-compose.yml
        fi 
    done
    echo "* Docker compose file generated"

    requestPeriod=0.1
    deploy_and_load $requestPeriod $invokeProbability $results
done 

# *******************************************
# EXPERIMENT 2.1: Varying failing services, based on failure cascade length
# (root causing service set to fail with probability 0.5, other services set to not fail on their own)
# (end-users' load set to send 10 requests/sec, invoke probability set to 0.5)
# *******************************************

echo ""
echo "========================="
echo "     Experiment 2.1"
echo "========================="
    
# create folder where to store the logs
results="logs_exp21_cascadeLength"
mkdir $results

rootCauses="frontend orders shipping rabbitMq"
for failingService in $rootCauses; do 	
    echo "FAILING SERVICE ${failingService}" 
    # generate docker-compose file with single point of failure 
    cp docker-compose.yml docker-compose.yml.original
    for service in $serviceList ; do
        # all services set to be replicated over 3 instances
        sed -i "s/${service^^}_REPLICAS/3/" docker-compose.yml
        # all services invoking backend services with probability 0.5
        sed -i "s/${service^^}_INVOKE/50/" docker-compose.yml
        # all services (but "failingService") not failing on their own
        if [ $service != $failingService ]; then
            sed -i "s/${service^^}_FAIL/0/" docker-compose.yml
        # shipping failing with probability 0.5
        else 
            sed -i "s/${service^^}_FAIL/50/" docker-compose.yml
        fi 
    done
    echo "* Docker compose file generated"

    requestPeriod=0.1
    deploy_and_load $requestPeriod $failingService $results
done 


# *******************************************
# EXPERIMENT 2.2: Varying failing services, based on failure probability
# (all services set to fail on with the same -varying- probability)
# (end-users' load set to send 10 requests/sec, invoke probability set to 0.5)
# *******************************************

echo ""
echo "========================="
echo "     Experiment 2.2"
echo "========================="
    
# create folder where to store the logs
results="logs_exp22_failProbability"
mkdir $results

failProbabilities="10 20 30 40 50 60 70"
for failProbability in $failProbabilities; do 	
    echo "FAILING PROBABILITY: ${failProbability}" 
    # generate docker-compose file with single point of failure 
    cp docker-compose.yml docker-compose.yml.original
    for service in $serviceList ; do
        # all services set to be replicated over 3 instances
        sed -i "s/${service^^}_REPLICAS/3/" docker-compose.yml
        # all services invoking backend services with probability 0.5
        sed -i "s/${service^^}_INVOKE/50/" docker-compose.yml
        # all services failing (on their own) with probability "failProbability"
        sed -i "s/${service^^}_FAIL/${failProbability}/" docker-compose.yml
    done
    echo "* Docker compose file generated"

    requestPeriod=0.1
    deploy_and_load $requestPeriod $failProbability $results
done 
