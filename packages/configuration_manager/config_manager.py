import yaml
import docker
import os
import git
import glob
import requests
import json
from git import Repo
from .config_worker import  ConfigWorker 
from .config_message import ConfigMessage 

class DTConfigurationManager:
    def __init__(self):
        self.robot_type = "unknown"
        self.docker_client =  docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.active_config = None
        self.config_path = None 
        self.module_path = "/data/assets/dt-architecture-data/modules/" 
        self.current_configuration = "none"
        self.dt_version = "ente"
        self.worker = ConfigWorker()
        self.status = ConfigMessage()

        if os.path.isfile("/data/config/robot_type"):
            self.robot_type = open("/data/config/robot_type").readline()
        elif os.path.isfile("/data/stats/init_sd_card/parameters/robot_type"):
            self.robot_type = open("/data/stats/init_sd_card/parameters/robot_type").readline()
        else:
            self.status["status"] = "error"
            self.status["message"] = "could not find robot type in expected paths"

        if not os.path.isdir("/data/assets/dt-architecture-data"):
            os.makedirs("/data/assets", exist_ok=True)
            git.Git("/data/assets").clone("git://github.com/duckietown/dt-architecture-data.git", branch=self.dt_version)

        if os.path.isdir("/data/assets/dt-architecture-data"): 
            self.config_path = "/data/assets/dt-architecture-data/configurations/"+self.robot_type
        

    def get_configuration_list (self):
        configurations = {}

        if self.config_path is not None:
            config_paths = glob.glob(self.config_path + "/*.yaml")
            configurations["configurations"] = [os.path.splitext(os.path.basename(f))[0] for f in config_paths]
        else:
            self.status["status"] = "error"
            self.status["message"].append("could not find configurations (dt-docker-data)")
            return self.status
        return configurations

    def stop_containers(self):
        return self.worker.stop_containers()

    def get_container_list(self):
        l = self.docker_client.containers.list()
        val = {}
        val["containers"] = {}
        for c in l:
            val["containers"][c.id]={ c.attrs['Config']['Image'] : c.status }

        return val

    def get_attributes(self):
        l = self.docker_client.images.list()
        val = {}
        for i in l:
            val[i.id] = i.labels
        return val

    def apply_configuration(self, config_name):
        data = self.get_configuration(config_name)

        return str(self.worker.apply_configuration(data))

    def apply_custom_configuration(self, config):
        return str(self.status)

    def get_job_status(self, id):
        if int(id) in self.worker.log:
            return self.worker.log[int(id)]
        else:
            return self.worker.log.copy()

    def get_status(self):
        return self.status.msg

    def get_configuration(self, config):
        path_to_config = self.config_path + "/" + config + ".yaml"
        try:
            with open(path_to_config, 'r') as f:
                data = yaml.load(f)
                if "modules" in data:
                    mods = data["modules"]
                    for m in mods:
                        if "type" in mods[m]:
                            modtype = mods[m]["type"]
                            mod_config = self.get_module(modtype)
                            if "configuration" in mod_config:
                                data["modules"][m]["configuration"] = mod_config["configuration"]
                return data
        except FileNotFoundError:
            error_msg = {}
            error_msg["status"] = "error"
            error_msg["message"] = "Configuration file not found " 
            error_msg["data"] = path_to_config
            return error_msg

    def get_configuration_status(self):
        return json.dumps(self.status)
    

    def get_module(self, module_name):
        try:
            with open(self.module_path+"/"+module_name+".yaml", 'r') as fd:
                module_info = yaml.load(fd)
                config = module_info["configuration"]

                # update ports for pydocker from docker-compose
                if "ports" in config:
                    ports = config["ports"]
                    newports = {}
                    for p in ports:
                        external,internal = p.split(":", 1)
                        newports[internal]=int(external)
                    config["ports"] = newports

                # update volumes for pydocker from docker-compose
                if "volumes" in config:
                    vols = config["volumes"]
                    newvols = {}
                    for v in vols:
                        host, container = v.split(":", 1)
                        newvols[host] = {'bind': container, 'mode':'rw'}
                    config["volumes"] = newvols

                # update restart_policy
                if "restart" in config:
                    config.pop("restart")
                    restart_policy = {"Name":"always"}

                # update container_name
                if "container_name" in config:
                    config["name"] = config.pop("container_name")

                if "image" in config:
                    config["image"] = config["image"].replace('${ARCH-arm32v7}','arm32v7' )

                return module_info
        except FileNotFoundError:
            error_msg = {}
            error_msg["status"] = "error"
            error_msg["message"] = "Module file not found" 
            error_msg["data"] = self.module_path + module_name + ".yaml"
            return error_msg

    def pull_image(self, url):
        return self.worker.pull_image(url) 

    def get_module_list(self):
        modules = {}
        yaml_paths = glob.glob(self.module_path + "/*.yaml")
        modules["modules"] = [] 
        for f in yaml_paths:
            try:
                with open(f, 'r') as fd:
                    print ("loading module: " + f)
                    config = yaml.load(fd)
                    filename, ext = os.path.splitext(os.path.basename(f))
                    modules["modules"].append(filename)
            except FileNotFoundError:
                error_msg = {}
                error_msg["status"] = "error"
                error_msg["message"] = "Module file not found" 
                error_msg["data"] = self.module_path + "/" + module_name + ".yaml"
                return error_msg
        return modules

    def clear_job_log(self):
        return self.worker.clear_log()

    def get_image_info(self, image):
        def get_config(image_name, reference):
            token_response = json.loads(requests.get('https://auth.docker.io/token?scope=repository:{}:pull&service=registry.docker.io'.format(image_name)).text)
            token = token_response["token"]
            headers = {
                    'Accept': 'application/vnd.docker.distribution.manifest.list.v2+json',
                    'Authorization': 'Bearer {}'.format(token)
            }

            url = 'https://registry-1.docker.io/v2/{}/manifests/{}'.format(image_name, reference)
            manifest_response = json.loads(requests.get(url, headers=headers).text)
            if int(manifest_response["schemaVersion"]) == 2:
                digest = manifest_response["config"]["digest"]
                headers = {'Authorization': 'Bearer {}'.format(token)}
                url = 'https://registry-1.docker.io/v2/{}/blobs/{}'.format(image_name, digest)
                config_response = json.loads(requests.get(url, headers=headers).text)
                config = config_response['container_config']
                return config, None
            else:
                config = json.loads(manifest_response["history"][0]["v1Compatibility"])["config"]
                return config, None

        def get_image_from_labels(labels):
            image_name, tag = None, None
            for label_key in labels.keys():
                if "base.image" in label_key:
                    if "ubuntu" in labels[label_key]:
                        image_name = labels[label_key]
                    else:
                        image_name = "duckietown/{}".format(labels[label_key])
                if "base.tag" in label_key:
                    tag = labels[label_key]
            if not image_name:
                return None
            if ":" in image_name:
                return image_name
            return "{}:{}".format(image_name, tag if tag else "latest")

        
        
        tag, sha = None, None

        if '@' in image:
            image_name, sha = image.split('@', 1)
        elif ':' in image:
            image_name, tag = image.split(':', 1)
        else:
            image_name = image
            tag = 'latest'    
        if '/' not in image_name:
            image_name = 'library/{}'.format(image_name)    
        reference = tag or sha
        data = {}

        base_config, error = get_config(image_name, reference)
        print(base_config)
        if error:
            return error
        labels = base_config["Labels"]
        data["image"] = image_name
        data["sha"] = base_config["Image"]
        data["Labels"] = labels
        anchestry = []
        base_image_name = get_image_from_labels(labels)
        while base_image_name:
            anchestry.append(base_image_name)
            base_image_name, base_tag = base_image_name.split(':', 1)
            base_image_config, error = get_config(base_image_name, base_tag)
            labels = base_image_config["Labels"]
            base_image_name = get_image_from_labels(labels)
            if "ubuntu" in base_image_name:
                anchestry.append(base_image_name)
                break

        data["anchestry"] = anchestry
        message = {
                    "status": "ok",
                    "message": None,
                    "data": data
            }
        return message
