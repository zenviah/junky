import os
from pathlib import Path
from datetime import datetime, timedelta

MAX_AGE = timedelta(weeks=1)

def remove_old_files(path, max_age, silent=True, require_confirmation=False):
    """
    Removes files from the provided directory that have a last modified time older than the time difference specified.

    :path: The path of the directory to search
    :max_time: The max age of files before they are deleted as an int or float in seconds or a datetime.timedelta object.
    :silent: Whether the function should run without terminal interaction (setting to False requires confimation from stdin). Defaults to true.
    """

    if type(max_age) != timedelta:
        max_age = timedelta(seconds=max_age)

    files = os.listdir(path)

    delete_files = []

    for f in files:
        f_path = Path(path,f)
        if os.path.isdir(f_path):
            continue

        metadata = os.stat(f_path)
        last_modified_time = datetime.fromtimestamp(metadata.st_mtime)

        current_time = datetime.now()

        last_modified_age = current_time - last_modified_time

        if last_modified_age > max_age:
            delete_files.append(f_path)

    n_files = len(delete_files)

    if n_files == 0:
        if not silent:
            print("No files to delete.")
        return

    if not silent:
        plural_char = "" if n_files == 1 else "s"

        print(f"Found {n_files} stale file{plural_char} in {path}.")

    if require_confirmation:
        while True:
            confirm = input("Are you sure you want to delete? (Y/n) ")
            if confirm.lower() in ('yes','y'):
                break
            elif confirm.lower() in ('no','n'):
                print("Aborted file deletion.")
                return
            else:
                print("Invalid input")

    for f in delete_files:
        try:
            os.remove(f)
        except Exception as e:
            if silent:
                raise e
            print(f"Skipping file {f}:\n{e}")

def clean_cwd():
    """
    Removes all files from the current working directory that have not been modified
    in over 7 days (MAX_AGE).
    """
    
    remove_old_files(os.getcwd(), MAX_AGE, silent=False, require_confirmation=True)
