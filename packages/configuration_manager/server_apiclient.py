from flask import Flask
from flask import request
import json

#This script uses the dt-commons library of dt-archapi-utils, instead of the
#files within dt-architecture-api. Not active unless .launch file is changed.
#The number of available endpoints is less those in dt-architecture-api.
from dt_archapi_utils import ArchAPIClient

#Initialize
app = Flask(__name__)
manager = ArchAPIClient()

#Default response
@app.route("/")
def home():
    return json.dumps(manager.default_response())


#Passive messages
@app.route("/configuration/list")
def configs():
    return json.dumps(manager.configuration_list())

@app.route("/configuration/status")
def status():
    return json.dumps(manager.configuration_status())

@app.route("/configuration/info/<config_name>", methods=['GET'])
def get_config(config_name):
    return json.dumps(manager.configuration_info(config_name))

@app.route("/module/list")
def modules():
    return json.dumps(manager.module_list())

@app.route("/module/info/<module_name>")
def get_module_info(module_name):
    return json.dumps(manager.module_info(module_name))


#Active messages
#IGNORE: dt-commons lib does not include required docker_client
'''
@app.route("/configuration/set/<config_name>", methods=['GET'])
def load_config(config_name):
    return json.dumps(manager.configuration_set_config(config_name))

@app.route("/pull/<image_name>")
def pull_image(image_name):
    return json.dumps(manager.pull_image(image_name))

@app.route("/monitor/<id>", methods=['GET'])
def get_job_status(id):
    return json.dumps(manager.monitor_id(id))
'''

#Define port and host for communication
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)
