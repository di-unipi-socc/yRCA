#!/bin/bash

serviceList="EDGEROUTER FRONTEND ORDERS ORDERSDB CATALOGUE CATALOGUEDB USERS USERSDB CARTS CARTSDB PAYMENT SHIPPING RABBITMQ QUEUEMASTER"

# download load script from "chaos-echo"
curl https://raw.githubusercontent.com/di-unipi-socc/chaos-echo/main/generate_workload.sh > generate_workload.sh
chmod ugo+x generate_workload.sh

for s in $serviceList; do
    # generate docker-compose file with single point of failure 
    # (service s failing, all other services s1 not failing)
    cp docker-compose.yml docker-compose.yml.original
    sed -i "s/${s}_FAIL/100/" docker-compose.yml
    for s1 in $serviceList ; do
        if [ $s != $s1 ]; then
            sed -i "s/${s1}_FAIL/0/" docker-compose.yml 
        fi 
    done

    # launch & load deployment
    docker stack deploy -c docker-compose.yml sockecho
    sleep 60
    ./generate_workload.sh -d 30 -p 0.1
    sleep 60
    docker stack rm sockecho

    # restore original docker file
    mv docker-compose.yml.original docker-compose.yml
done
