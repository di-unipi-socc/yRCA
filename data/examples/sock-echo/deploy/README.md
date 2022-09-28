# Sock Echo deployment
To configure a deployable instance of Sock Echo, please issue:
```
python3 config.py SERV1 [SERV2 SERV3 ...]
```
where `SERVx` are the names of the services to be configured to fail with 10% probability

The obtained instance can then be deployed by issuing:
```
docker stack deploy -c docker-compose-configured.yml sockecho
```