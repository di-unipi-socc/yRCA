#!/bin/bash

serviceList="EDGEROUTER FRONTEND ORDERS ORDERSDB CATALOGUE CATALOGUEDB USERS USERSDB CARTS CARTSDB PAYMENT SHIPPING RABBITMQ QUEUEMASTER"

# download load script from "chaos-echo"
curl https://raw.githubusercontent.com/di-unipi-socc/chaos-echo/main/deploy/examples/sock-echo/logstash.conf > logstash.conf
curl https://raw.githubusercontent.com/di-unipi-socc/chaos-echo/main/generate_workload.sh > generate_workload.sh
chmod ugo+x generate_workload.sh

# s="ORDERS" 			# uncomment for single run 
for s in $serviceList; do 	# comment for single run
    # generate docker-compose file with single point of failure 
    # (service s failing, all other services s1 not failing)
    cp docker-compose.yml docker-compose.yml.original
    sed -i "s/${s}_FAIL/50/" docker-compose.yml
    for s1 in $serviceList ; do
        if [ $s != $s1 ]; then
            sed -i "s/${s1}_FAIL/0/" docker-compose.yml 
        fi 
    done

    echo ""
    cat  docker-compose.yml
    echo ""
    # launch & load deployment
    docker stack deploy -c docker-compose.yml sockecho
    sleep 30
    ./generate_workload.sh -d 15 -p 0.5
    sleep 30
    docker stack rm sockecho

    # restore original docker file
    mv docker-compose.yml.original docker-compose.yml
done 				#comment for single run
