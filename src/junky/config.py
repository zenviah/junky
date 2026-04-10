import tomllib
from collections import deque
from datetime import timedelta, datetime
import os

TIMES = ('seconds','minutes','hours','days','weeks')

class Config:
    def __init__(self):
        self.config = {}
        pass

    def load_from_file(self,filename):
        with open(filename, 'rb') as f:
            self.config = tomllib.load(f)
        return self

    def write_to_file(self,filename=".junky"):
        with open(filename, "w") as f:
            queue = deque(self.config.items())
            current_level = ''
            while len(queue) != 0:
                k, v = queue.popleft()

                if v is None:
                    if k is None:
                        current_level = ''
                    else:
                        current_level = k
                        f.write("\n["  + current_level + "]\n")
                elif type(v) == dict:
                    if current_level:
                        queue.append((current_level + '.' + k,None))
                    else:
                        queue.append((k, None))
                    queue.extend(v.items())
                    queue.append((None,None))

                else:
                    full_value = f'"{v}"' if type(v) == str else v
                    f.write(f'{k} = {full_value}\n')

    def get_removal_criteria(self):
        return RemovalCriteria(self.config.get("remove"))

class RemovalCriteria:
    def __init__(self, config_dict={}):
        age_config = config_dict.get("max_age")
        if age_config:
            self.max_age_parameter = age_config.get("parameter","last_modified")
            times = {k: v for k, v in age_config.items() if k in TIMES}

            self.max_age = timedelta(**times)
        else:
            self.max_age = None
            self.max_age_parameter = None
        
        self.ignore_files = config_dict.get("ignore",{"files":False}).get("files",False)
        self.ignore_dirs = config_dict.get("ignore",{"dirs":True}).get("dirs",True)

    def meets_criteria(self, dir_entry: os.DirEntry) -> bool:
        #Check if .junky
        if dir_entry.name == ".junky":
            return False

        #Check if ignored as a file/dir
        if self.ignore_files and dir_entry.is_file():
            return False
        elif self.ignore_dirs and dir_entry.is_dir():
            return False
        
        
        #Check age settings
        if self.max_age:
            stat = dir_entry.stat()
            
            if self.max_age_parameter == 'last_modified':
                file_time = stat.st_mtime
            elif self.max_age_parameter == 'created':
                file_time = stat.st_ctime
            elif self.max_age_parameter == 'last_accessed':
                file_time = stat.st_atime
            else:
                raise ValueError(f'Max age paremeter set to "{self.max_age_parameter}". Should be one of "created", "last_modified", or "last_accessed".')
            
            file_age = datetime.now() - datetime.fromtimestamp(file_time)

            if file_age > self.max_age:
                return True

        return False

    def get_candidates(self, dir="."):
        """
        Get candidates for deletion
        """

        return [i.path for i in os.scandir(dir) if self.meets_criteria(i)]
    
    def set_max_age(self, age: timedelta, age_parameter = "last_modified"):
        self.max_age = age
        self.max_age_parameter = age_parameter
        return self
    
    def as_dict(self):
        out = {}
        if self.age:
            out["max_age"] = {
                "days": self.max_age.days,
                "seconds": self.max_age.seconds,
                "parameter": self.max_age_parameter
            }
            
        out["ignore"] = {
            "files": self.ignore_files,
            "dirs": self.ignore_dirs
        }

        return out

