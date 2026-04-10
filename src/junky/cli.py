from . import cleanup
from .config import Config, RemovalCriteria

import os

def main():
    if os.path.exists(".junky"):
        config = Config().load_from_file(".junky")
        rc = config.get_removal_criteria()
        cleanup.remove_files(os.getcwd(),rc)
    else:
        cleanup.clean_cwd()


