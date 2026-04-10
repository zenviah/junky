import os
from pathlib import Path
from datetime import datetime, timedelta
from .config import RemovalCriteria

MAX_AGE = timedelta(weeks=1)

def remove_files(path, removal_critera: RemovalCriteria, silent=True, require_confirmation=False):
    """
    Removes files from the provided directory that have a last modified time older than the time difference specified.

    :path: The path of the directory to search
    :removal_criteria: A junky.config.RemovialCriteria object defining which files should be deleted.
    :silent: Whether the function should run without profiding feedback to stdout. Defaults to True.
    :require_confirmation: Whether the function requires confirmation from stdin. Defaults to False.
    """

    if not isinstance(removal_critera, RemovalCriteria):
        raise TypeError(f"Expected type RemovalCritera, got {type(removal_critera)}")

    delete_files = removal_critera.get_candidates()

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
        p = Path(f)
        if p.is_file():
            try:
                os.remove(f)
            except Exception as e:
                if silent:
                    raise e
                print(f"Skipping file {f}:\n{e}")
        elif p.is_dir():
            p.rmdir()

def clean_cwd():
    """
    Removes all files from the current working directory that have not been modified
    in over 7 days (MAX_AGE).
    """
    
    remove = RemovalCriteria().set_max_age(MAX_AGE)

    remove_files(os.getcwd(), remove, silent=False, require_confirmation=True)
