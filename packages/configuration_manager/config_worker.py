import docker
import os
import time
from multiprocessing import Process, Manager
from .config_message import JobLog

'''
    The following functions are spawned by the worker as a sub process.  
    They log is constantly re-assigned since it is DictProxy() used to
    share the task status across processes and it only updates upstream
    when it is reassigned and not on updates to the nested dictionary.  

'''
def stop_containers_proc(log):
    pid = os.getpid()
    docker_client =  docker.DockerClient(base_url='unix://var/run/docker.sock')
    progress = JobLog(pid)
    log[pid] = progress.log 
    me = "duckietown/dt-architecture-api"
    l = docker_client.containers.list()

    for c in l:
        image = c.attrs['Config']['Image']
        if not image.startswith(me):
            try: 
                progress.record("stopping " + str(image))
                c.stop()
                progress.record("stopped " + str(image))
                log[pid] = progress.log
                time.sleep(30)
            except docker.errors.APIError as error:
                progress.error_out(str(error))
                log[pid] = progress.log
                return False
    progress.complete()
    log[pid] = progress.log
    return True

def apply_config_proc(modules, log):
    pid = os.getpid()
    docker_client = docker.DockerClient(base_url="unix://var/run/docker.sock")
    progress = JobLog(pid)
    progress.record("stopping all running containers")
    log[pid] = progress.log
    if stop_containers_proc(log):
        progress.record("Succeeded in stopping all containers")
        if "modules" in modules:
            mods = modules["modules"]
            total_number = len(mods)
            counter = 0
            for m in mods:
                progress.record("Starting " + m)
                counter = counter + 1 
                if "configuration" in mods[m]:
                    try:
                        config = mods[m]["configuration"]
                        container = docker_client.containers.run(detach=True, **config)
                        progress.record("Started " + m)
                    except docker.errors.APIError as error:
                         progress.record("Docker error when starting " + m + " : " + str(error) + "\n" + str(config))
                         log[pid] = progress.log
                else:
                    progress.record("No configuration for module " + m + " : " + " skipping")

                progress.update_progress((counter/total_number ) * 100)
                log[pid] = progress.log
                time.sleep(10)

            progress.complete()
            log[pid] = progress.log
        else:
            progress.error("No modules provided in configuration provided")
            log[pid] = progress.log
    else:
        progress.error("failed to stop all running containers")
        log[pid] = progress.log

def pull_image_proc(url, log):
    pid = os.getpid()
    docker_client = docker.DockerClient(base_url="unix://var/run/docker.sock")
    progress = JobLog(pid)
    log[pid] = progress.log
    if ":" in url:
        image_url, image_tag = url.split(":",1)
    else:
        image_url = url
        image_tag = "latest"
    try:
        progress.record("pulling " + image_url + ":" + image_tag)
        docker_client.images.pull(image_url, tag=image_tag ) 
        progress.complete()
        log[pid] = progress.log 
    except docker.errors.APIError as error:
        progress.error(str(error))
        log[pid] =  progress.log

class ConfigWorker:
    def __init__(self):
        self.docker_client =  docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.manager = Manager()
        self.log = self.manager.dict()
        self.proc = None

    def clear_log(self):
        self.log.clear()
        c = ConfigMessage()
        return c.msg

    def pull_image(self, image_url):
        if self.proc is None or not self.proc.is_alive():
            self.proc = Process(target=pull_image_proc, args=(image_url,self.log,))
            self.proc.start()
            return str(self.proc.pid)
        else:
            return "busy"

    def apply_configuration(self, modules):
        if self.proc is None or not self.proc.is_alive():
            self.proc = Process(target=apply_config_proc, args=(modules, self.log,))
            self.proc.start()
            response = {}
            response["jobid"] = self.proc.pid
            return response
        else:
            return "busy"

    def status(self, pid):
        return self.busy

    def apply_custom_configuration(self, module_list):
        return ConfigMessage("ok", "not implemented yet")

    def stop_containers(self):
        if self.proc is None or not self.proc.is_alive():
            self.proc = Process(target=stop_containers_proc, args=(self.log,))
            self.proc.start()
            response = {"jobid": self.proc.pid}

            return response

        return "busy" 
