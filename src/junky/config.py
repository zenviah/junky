import tomllib
from datetime import timedelta, datetime
import os

class Config:
    def __init__(self):
        pass

    def load_from_file(self,filename):
        with open(filename) as f:
            self.config = tomllib.load(f)

    def write_to_file(self,filename=".junky"):
        pass

    def get_removal_criteria(self):
        return RemovalCriteria(self.config.get("remove"))

class RemovalCriteria:
    def __init__(self, config_dict={}):
        age_config = config_dict.get("max_age")
        if age_config:
            self.max_age_parameter = age_config.get("parameter","last_modified")
            times = {k: v for k, v in age_config.items() if k in ('seconds','minutes','hours','days','weeks')}

            self.max_age = timedelta(**times)
        else:
            self.max_age = None
            self.max_age_parameter = None
        
        self.ignore_files = config_dict.get("ignore",False).get("files",False)
        self.ignore_dirs = config_dict.get("ignore",True).get("files",True)

    def meets_criteria(self, dir_entry: os.DirEntry) -> bool:
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


    def get_candidates(self, dir=""):
        """
        Get candidates for deletion
        """

        return [i.path() for i in os.scandir(dir) if self.meets_criteria(i)]

