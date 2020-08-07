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


#DEVICE CONFIGURATION##########################################################
@app.route("/device/")
def home():
    return json.dumps(device_manager.default_response())

@app.route("/device/configuration/status")
def config_status():
    return json.dumps(device_manager.configuration_status())
@app.route("/device/configuration/list")
def config_list():
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
@app.route("/device/clearance")
def clearance_to_go():
    return json.dumps(device_manager.clearance())

@app.route("/device/configuration/set/<config_name>", methods=['GET'])
def load_config(config_name):
    return json.dumps(device_manager.configuration_set_config(config_name))
@app.route("/device/pull/<image_name>")
def pull_image(image_name):
    return json.dumps(device_manager.pull_image(image_name))
@app.route("/device/monitor/<id>", methods=['GET'])
def get_job_status(id):
    return json.dumps(device_manager.monitor_id(id))
@app.route("/device/image/info/<path:image_name>", methods=['GET'])
def image_info(image_name):
    return json.dumps(device_manager.get_image_info(image_name))
@app.route("/device/clearlogs")
def clear_logs():
    return json.dumps(device_manager.clear_job_log())


#FLEET CONFIGURATION############################################################
@app.route("/fleet/<fleet>")
def fleet_home(fleet):
    return json.dumps(fleet_manager.default_response(fleet))

@app.route("/fleet/configuration/info/<config_name>", methods=['GET'])
def fleet_get_config(config_name):
    return json.dumps(fleet_manager.configuration_info(config_name))
@app.route("/fleet/info/<fleet>", methods=['GET'])
def fleet_get_info(fleet):
    return json.dumps(fleet_manager.info_fleet(fleet))
@app.route("/fleet/configuration/status/<fleet>", methods=['GET'])
def fleet_get_config_status(fleet):
    return json.dumps(fleet_manager.configuration_status(fleet))

@app.route("/fleet/configuration/set/<config_name>/<fleet>", methods=['GET'])
def fleet_load_config(config_name, fleet):
    return json.dumps(fleet_manager.configuration_set_config(config_name, fleet))
@app.route("/fleet/monitor/<id>/<fleet>", methods=['GET'])
def fleet_get_job_status(id, fleet):
    return json.dumps(fleet_manager.monitor_id(id, fleet))

################################################################################


"""
#Passive messaging
@app.route("/fleet/configuration/list/<fleet>")
def fleet_configs(fleet):
    return json.dumps(fleet_manager.configuration_list(fleet))
#Active messaging
@app.route("/fleet/pull/<image_name>/<fleet>")
def fleet_pull_image(image_name, fleet):
    return json.dumps(fleet_manager.pull_image(image_name, fleet))

@app.route("/fleet/list/<fleet>")
def fleet_get_device_list():
    return json.dumps(fleet_manager.list())
@app.route("fleet/info/<fleet>")
def fleet_get_fleet_info(fleet):
    return json.dumps(fleet_manager.info(fleet))
@app.route("fleet/image/status/<fleet>")
def fleet_get_image_status():
    return json.dumps(fleet_manager.image_status())
@app.route("fleet/scan/<fleet>")
def fleet_scan_for_devices():
    return json.dumps(fleet_manager.scan())
@app.route("/fleet/clearlogs/<fleet>")
def fleet_clear_logs():
    return json.dumps(fleet_manager.clear_job_log())
"""


#Initialize
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
