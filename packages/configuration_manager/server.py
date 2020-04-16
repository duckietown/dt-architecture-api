from flask import Flask
from flask import request
import json

from .config_manager import DTConfigurationManager

#Initialize
app = Flask(__name__)

manager = DTConfigurationManager()

#Default response
@app.route("/")
def home():
    return json.dumps(manager.get_status())

#Passive messaging
@app.route("/configuration/list")
def configs():
    return json.dumps(manager.get_configuration_list())

@app.route("/configuration/status")
def status():
    return json.dumps(manager.get_configuration_status())

@app.route("/configuration/info/<config_name>", methods=['GET'])
def get_config(config_name):
    return json.dumps(manager.get_configuration(config_name))

@app.route("/module/list")
def modules():
    return json.dumps(manager.get_module_list())

@app.route("/module/info/<module_name>")
def get_module_info(module_name):
    return json.dumps(manager.get_module(module_name))


#Active messaging
@app.route("/configuration/set/<config_name>", methods=['GET'])
def load_config(config_name):
    return json.dumps(manager.apply_configuration(config_name))

@app.route("/configuration/set", methods=['POST'])
def set_config():
    return json.dumps(manager.apply_custom_configuration.form.get('config'))

@app.route("/pull/<image_name>")
def pull_image(image_name):
    return json.dumps(manager.pull_image(image_name))

@app.route("/monitor/<id>", methods=['GET'])
def get_job_status(id):
    return json.dumps(manager.get_job_status(id))


#Other endpoints (not yet documented)
@app.route("/containers")
def containers():
    return json.dumps(manager.get_container_list())

@app.route("/attributes")
def attributes():
    return json.dumps(manager.get_attributes())

@app.route("/stop")
def stop_containers():
    return json.dumps(manager.stop_containers())

@app.route("/clearlogs")
def clear_logs():
    return json.dumps(manager.clear_job_log())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083)
