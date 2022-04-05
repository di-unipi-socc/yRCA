# yRCA
**yRCA** enables identifying the possible root causes for a (failure) event to happen in a service instance in a multi-service application, only based on the application logs.

## How to Run yRCA
**yRCA** provides a Python3-based command-line interface, which can be run with the following command:
```
python3 yrca.py [OPTIONS] EVENT LOGS TEMPLATES
```
where
* `EVENT` is the path to the file containing the logged event that is to be explained (e.g., [event-edgeRouter.log](https://github.com/di-unipi-socc/yRCA/blob/main/data/examples/sock-echo/orders-fail/event-edgeRouter.log)),
* `LOGS` is the path to the file containing the logged events to be considered for explaining `EVENT`, viz., for finding the possible failure cascades causing `EVENT` to happen (e.g., [all.log](https://github.com/di-unipi-socc/yRCA/blob/main/data/examples/sock-echo/orders-fail/all.log)), and 
* `TEMPLATES` is the path to a YAML file specifying the templates for parsing logged events and assigning them with a type (e.g., [chaos-echo.yml](https://github.com/di-unipi-socc/yRCA/blob/main/data/templates/chaos-echo.yml))

By default, **yRCA** finds all possible explanations,  viz., the failure cascades that may have possibly caused `EVENT` to happen.
It then returns the possible explanations grouped based on their structure, and it ranks the returned explanation groups based on the frequency with which they occur).
**yRCA** can anyhow be configured with the available CLI `OPTIONS`, viz.,
* `--help` to print a help on the usage of yrca.py,
* `-v` or `--vebose`, to run **yRCA** in verbose mode (viz., to not group identified explanations but rather return them plain),
* `-n N` or `--nSols=N`, to set the number `N` of possible explanations to identify, and
* `-r X` or `--root=X` to require `X` to be the root causing service of identified explanations.

## How yRCA Works

**yRCA** is composed of two main components, viz., the `parser` and the `explainer`, which are invoked in sequence by the main module (`explain`), which implements the command-line interface.

### The Parser
The `parser` provides a function `parseEvents` for parsing a file `applicationLogs`, containing events logged by  service instances in the considered run of a multi-service application. An example of logged event is the following:
```
{
  "message":"2021-09-28 14:14:18.796 ERROR 1 --- [p-nio-80-exec-7] d.u.s.chaosecho.EchoServiceController    : Failing to contact frontend (request_id: [712399e1-b5ff-42b7-9a3b-2d9293fbeca7]). Root cause: org.springframework.web.client.HttpServerErrorException$InternalServerError: 500 : [{\"hash\":-1898628045,\"content\":\"Failing to contact backend services\"}]",
  "version":"1.1",
  "severity":"ERROR",
  "source_host":"10.0.0.2",
  "pid":"1",
  "@version":"1",
  "created":"2021-09-28T14:13:23.14966049Z",
  "timestamp":"2021-09-28 14:14:18.796",
  "event":"Failing to contact frontend (request_id: [712399e1-b5ff-42b7-9a3b-2d9293fbeca7]). Root cause: org.springframework.web.client.HttpServerErrorException$InternalServerError: 500 : [{\"hash\":-1898628045,\"content\":\"Failing to contact backend services\"}]",
  "tag":"edgeRouter",
  "container_name":"sockecho_edgeRouter.1.yhoejj5k0f2uc8lzcollgeala",
  "@timestamp":"2021-09-28T14:14:18.796Z",
  "container_id":"737b523ff95e5860eea879cc5bc9bc34d9ac7f11487b797e47f6705ec56e3ed9",
  "class":"d.u.s.chaosecho.EchoServiceController",
  "tags":["spring_boot"]
 }
```
whose fields `severity`, `container_name`, `event`, `message`, `timestamp`, and `@timestamp` are used by `parseEvents` to elicit information on the logged event. Based on such information, `parseEvents` generates a representation of logged events in Prolog, e.g,
```
log(edgeRouter,sockecho_edgeRouter_1,1632831258.796,timeout(frontend,'712399e1-b5ff-42b7-9a3b-2d9293fbeca7'),'Failing to contact frontend (request_id: [712399e1-b5ff-42b7-9a3b-2d9293fbeca7]). Root cause: org.springframework.web.client.HttpServerErrorException$InternalServerError: 500 : [{"hash":-1898628045,"content":"Failing to contact backend services"}]',err).
```
and puts it in a given `targetFile`. The latter can either be the `knowledgeBase` corresponding to all logged events or the `event` to be explained. 


To enable parsing any type of log file, the `parser` exploits log templating, viz., it imports a `parse` function from the [templater](parser/templater) module. 
The latter implements all the logic needed to parse log events based on the input `TEMPLATES` (see above). 
Example of templates for the [Chaos Echo](https://github.com/di-unipi-socc/chaos-echo) benchmarking application can be found in [data/templates](data/templates).

Other templates can be provided for parsing the logs of other applications, provided that they are given as a YAML file structured as follows:
```
client_send: [list_of_regex]
client_receive: [list_of_regex]
client_error: [list_of_regex]
client_timeout: [list_of_regex]
server_receive: [list_of_regex]
server_send: [list_of_regex]
```

### The Explainer
The `explainer` essentially takes the Prolog representation of the input files generated by the `parser` and runs a Prolog query to identify the desired explanations. The latter is done by running the Prolog program [`explain.pl`](explainer/prolog/explain.pl), which provides all the rules for identifying the desired amount of explanations for a given event.
