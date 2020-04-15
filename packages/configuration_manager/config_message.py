import datetime

class ConfigMessage:
    def __init__(self, status="ok", message=None, data=None):
        self.msg = {}
        self.msg["status"] = status
        self.msg["message"] = message
        self.msg["data"] = data

    def set_status(self, new_status):
        self.msg["status"] = new_status

    def __str__(self):
        return self.msg

class JobLog:
    def __init__(self, id):
        self.log = {}
        self.log["id"] = id
        self.log["status"] = "processing"
        self.log["progress"] = 0
        self.log["log"] = {}
        self.log["time_started"] = str(datetime.datetime.now())

    def record(self, message):
        self.log["log"][str(datetime.datetime.now())] = message

    def update_progress(self, new_value):
        if new_value >= 0 and new_value <= 100:
            self.log["progress"] = int(new_value)

    def cancel(self):
        self.log["status"] = "terminated"
        self.record("cancelled")
        self.log["time_finished"] = str(datetime.datetime.now())

    def error(self, msg):
        self.log["status"] = "error"
        self.record("Error: " + msg)
        self.update_progress(100)
        self.log["time_finished"] = str(datetime.datetime.now())

    def complete(self):
        self.log["status"] = "complete"
        self.record("completed")
        self.log["time_finished"] = str(datetime.datetime.now())
        self.update_progress(100)

    def __str__(self):
        return self.log
