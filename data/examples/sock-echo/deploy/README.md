# Sock Echo deployment
To configure a deployable instance of Sock Echo, please issue:
```
python3 config.py [-p PERCENTAGE] SERV1 [SERV2 SERV3 ...]
```
where `SERVx` are the names of the services to be configured to fail with given probability. 
If option `-p PERCENTAGE` is specified, the failure probability is set to `PERCENTAGE`; otherwise, it is set to 10% by default.

The obtained instance can then be deployed by issuing:
```
docker stack deploy -c docker-compose-configured.yml sockecho
```
and it can be loaded with the [load generator script](https://github.com/di-unipi-socc/chaos-echo/blob/main/generate_workload.sh) publicly available in [Chaos Echo's repository](https://github.com/di-unipi-socc/chaos-echo).