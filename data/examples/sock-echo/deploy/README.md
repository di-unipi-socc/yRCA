# Sock Echo deployment
To configure a deployable instance of Sock Echo, please issue:
```
python3 config.py [-i INVOKE_PERCENTAGE] [-f FAILURE_PERCENTAGE] [-c CRASH_PERCENTAGE] [-r REPLICAS] SERV1 [SERV2 SERV3 ...]
```
where `SERVx` are the names of the services to be configured to fail with given probability. 
* If option `-i INVOKE_PERCENTAGE` is specified, each application service (other than `edgeRouter`) is set to invoked its backend services with probability `INVOKE_PERCENTAGE`; otherwise, such probability is set to 75% by default.
* If option `-f FAILURE_PERCENTAGE` is specified, the probability for the listed services `SERVx` to fail in handling an incoming request is set to `FAILURE_PERCENTAGE`; otherwise, such probability is set to 10% by default.
* If option `-c CRASH_PERCENTAGE` is specified, the probability for the listed services `SERVx` to crash (simulating unrecoverable errors) is set to `CRASH_PERCENTAGE`; otherwise, such probability is set to 10% by default.
* If option `-r REPLICAS` is specified, each application service (other than `edgeRouter`) is set to be replicated into the given number `REPLICAS` of instance; otherwise, one instance of each of such services is deployed by default.

The obtained instance can then be deployed by issuing:
```
docker stack deploy -c docker-compose-configured.yml sockecho
```
and it can be loaded with the [load generator script](https://github.com/di-unipi-socc/chaos-echo/blob/main/generate_workload.sh) publicly available in [Chaos Echo's repository](https://github.com/di-unipi-socc/chaos-echo).