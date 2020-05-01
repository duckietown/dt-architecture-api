#!/usr/bin/env python3

import json
import docker

from flask import Flask
from flask import request
from dt_archapi_utils import ArchAPIClient
from dt_multi_archapi_utils import MultiArchAPIClient

#Initialize
app = Flask(__name__)
port = 8083 # /architecture
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

device_manager = ArchAPIClient(client=client)
fleet_manager = MultiArchAPIClient(client=client, port=str(port))


#DEVICE CONFIGURATION
#Default response
@app.route("/device/")
def home():
    return json.dumps(device_manager.default_response())

#Passive messaging
@app.route("/device/configuration/list")
def configs():
    return json.dumps(device_manager.configuration_list())
@app.route("/device/configuration/info/<config_name>", methods=['GET'])
def get_config(config_name):
    return json.dumps(device_manager.configuration_info(config_name))
@app.route("/device/module/list")
def modules():
    return json.dumps(device_manager.module_list())
@app.route("/device/module/info/<module_name>")
def get_module_info(module_name):
    return json.dumps(device_manager.module_info(module_name))

#Active messaging
@app.route("/device/configuration/set/<config_name>", methods=['GET'])
def load_config(config_name):
    return json.dumps(device_manager.configuration_set_config(config_name))
@app.route("/device/pull/<image_name>")
def pull_image(image_name):
    return json.dumps(device_manager.pull_image(image_name))
@app.route("/device/monitor/<id>", methods=['GET'])
def get_job_status(id):
    return json.dumps(device_manager.monitor_id(id))
@app.route("/device/clearlogs")
def clear_logs():
    return json.dumps(device_manager.clear_job_log())



#FLEET CONFIGURATION
#Default response
@app.route("/fleet/")
def home():
    return json.dumps(fleet_manager.default_response())

"""
#Passive messaging
@app.route("/fleet/configuration/info/<config_name>", methods=['GET'])
def get_config(config_name):
    return json.dumps(fleet_manager.configuration_info(config_name))

#Active messaging
@app.route("/fleet/configuration/set/<config_name>", methods=['GET'])
def load_config(config_name):
    return json.dumps(fleet_manager.configuration_set_config(config_name))
@app.route("/fleet/pull/<image_name>")
def pull_image(image_name):
    return json.dumps(fleet_manager.pull_image(image_name))
@app.route("/fleet/monitor/<id>", methods=['GET'])
def get_job_status(id):
    return json.dumps(fleet_manager.monitor_id(id))
@app.route("/fleet/list")
def get_device_list():
    return json.dumps(fleet_manager.list())
@app.route("fleet/info/<fleet>")
def get_fleet_info(fleet):
    return json.dumps(fleet_manager.info(fleet))
@app.route("fleet/image/status")
def get_image_status():
    return json.dumps(fleet_manager.image_status())
@app.route("fleet/scan")
def scan_for_devices():
    return json.dumps(fleet_manager.scan())
@app.route("/fleet/clearlogs")
def clear_logs():
    return json.dumps(fleet_manager.clear_job_log())
"""


#Initialize
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
