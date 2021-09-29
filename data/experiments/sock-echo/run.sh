#!/bin/bash

serviceList="edgeRouter frontend orders ordersDb catalogue catalogueDb users usersDb carts cartsDb payment shipping rabbitMq"

# download load script from "chaos-echo"
curl https://raw.githubusercontent.com/di-unipi-socc/chaos-echo/main/deploy/examples/sock-echo/logstash.conf --silent > logstash.conf
curl https://raw.githubusercontent.com/di-unipi-socc/chaos-echo/main/generate_workload.sh --silent > generate_workload.sh
chmod ugo+x generate_workload.sh

# create folder where to store results
results="results_$(date +%y_%m_%d_%H_%M)"
mkdir $results

# s="orders" 			# uncomment for single run 
for s in $serviceList; do 	# comment for single run
    echo ""
    echo "==================================="
    echo "     Service: ${s}"
    echo "==================================="
    # generate docker-compose file with single point of failure 
    # (service s failing, all other services s1 not failing)
    cp docker-compose.yml docker-compose.yml.original
    sed -i "s/${s^^}_FAIL/0/" docker-compose.yml
    for s1 in $serviceList ; do
        if [ $s != $s1 ]; then
            sed -i "s/${s1^^}_FAIL/0/" docker-compose.yml 
        fi 
    done
    echo "* Docker compose file generated"

    #launch & load deployment
    echo "* Docker deployment started" 
    docker stack deploy -c docker-compose.yml sockecho
    sleep 60
    echo "* Docker deployment completed"
    echo "* Generating workload"
    fault=0
    while [ $fault -eq 0 ] # loop until at least one frontend failure happened
    do
        curlLog="${s}-curl.log"
        ./generate_workload.sh -d 15 -p 0.5 > $curlLog
        fault=$(grep 500 $curlLog | wc -l)
        echo "Generated faults: ${fault}"
    done
    sleep 30
    echo "* Undeployment started"
    docker stack rm sockecho
    echo "* Undeployment completed"

    # save logs
    grep ERROR echo-stack.log | grep _edgeRouter | tail -n 1 > $s-edgeRouter-fault.log
    grep ERROR echo-stack.log | grep _$s | tail -n 1 > $s-$s-fault.log
    mv echo-stack.log $s-all.log
    mv *.log $results
    echo "* Log files stored in ${results}"

    # analyse logs
    echo "* Log analysis started"
    cd ../../.. # move to main project folder
    sockecho="data/experiments/sock-echo"
    python3 explain.py $sockecho/$results/$s-edgeRouter-fault.log $sockecho/$results/$s-all.log > $sockecho/$results/$s-edgeRouter-fault.output
    python3 explain.py $sockecho/$results/$s-$s-fault.log $sockecho/$results/$s-all.log > $sockecho/$results/$s-$s-fault.output
    cd $sockecho # get back to sockecho experiment folder
    echo "* Log analysis completed (outputs stored in ${results})"

    # restore original docker file
    mv docker-compose.yml.original docker-compose.yml
    echo "* Original log file restored"
done 				#comment for single run
