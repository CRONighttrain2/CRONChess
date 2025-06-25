import time

class Logger:
    def __init__(self, log_url: str, clear_log: bool):
        self.log_start = time.time()
        self.tasks: dict = dict()
        if clear_log:
            self.log_file = open(log_url, "w")
            self.log_file.write("")
            self.log_file.close()
        self.log_file = open(log_url, "a")

    def write_to_file(self, new_text: str, indent):
        self.log_file.write("\t" * indent + new_text + "\n")

    def start_task(self, task_name: str, indent):
        st = time.time()
        self.tasks[task_name] = [st, 0]

    def end_task(self,task_name:str, indent):
        et = time.time()
        if task_name in self.tasks.keys():
            st = self.tasks[task_name][0]
            self.tasks[task_name][1] += et
            tt = et - st
            self.write_to_file(task_name + "," + str(tt), indent)

    def review_logs(self):
        self.log_file.close()
        #      [objname,[functName,[functTime,timesFunctRan]]]
        objects: dict[str, dict[str,list[float]]] = dict(dict())
        file = open(self.log_file.name,"r")
        for line in file:
            log = line.strip()
            log = log.split(",")
            name = log[0]
            obj_name = name.split(" ")[0].replace("<","")
            funct_name = name.split(".")[len(name.split(".")) - 1]
            funct_time = float(log[len(log) - 1])
            if not obj_name in objects.keys():
                objects[obj_name] = dict()
            if not funct_name in objects[obj_name].keys():
                objects[obj_name][funct_name] = [0,0]
            objects[obj_name][funct_name][0] += funct_time
            objects[obj_name][funct_name][1] += 1
        et = time.time()
        print("log started: " + str(self.log_start) + " seconds, log ended: " + str(et) + " seconds, log took:" + str(et - self.log_start) + " seconds")
        for obj in objects.keys():
            obj_time: float = 0
            for subtask in objects[obj].keys():
                obj_time += objects[obj][subtask][0]
            print("\t object: " + obj + " ran for: " + str(obj_time) + " seconds")
            for subtask in objects[obj].keys():
                print("\t\t" + subtask + " ran for: " + str(objects[obj][subtask][0]) + " seconds, and ran: " + str(objects[obj][subtask][1]) + " times, with an average runtime of: " + str(objects[obj][subtask][0]/objects[obj][subtask][1]) + " seconds")
        file.close()

    def close_file(self):
        self.review_logs()