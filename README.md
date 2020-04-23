# Duckietown Architecture API

## Description
Providing REST endpoints for configuration management of duckietown devices.  Runs on port `8083`.  The endpoints all return a JSON response.  These endpoints are currently in-progress and may change as the project evolves.  Using the ente version of duckietown shell.

API data is found in the [dt-architecture-data](https://github.com/duckietown/dt-architecture-data) respository.

## How to build
`dts devel build -f --arch arm32v7 -H <device_host_name>` <!-- --force -->

## How to run
`docker -H  <device_host_name> run -it --rm --network="host"  -v /data:/data -v /var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket -v /var/run/docker.sock:/var/run/docker.sock  duckietown/dt-architecture-api:ente-arm32v7`

## Current endpoints
From a browser, enter `DEVICE_NAME.local:8083/` followed by one of the following endpoints:

### /device
- `/` : status of configuration manager  
- `/module/list`  :  list of all module names  
- `/module/info/<module>` : module details  

- `/configuration/list` : list of all configurations available  
- `/configuration/info/<configuration>` :  configuration details  
- `/configuration/set/<configuraion>` : applies configuration
- `/pull/<image_name>` : pulls a docker image to the device  
- `/monitor/<id>` : get status of a job  

### /fleet
- none
