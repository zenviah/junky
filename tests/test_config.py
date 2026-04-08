from junky.config import Config, RemovalCriteria
from datetime import datetime, timedelta
import os

# Helper functions
def create_dummy_files(filenames):
    for filename in filenames:
        with open(filename,'w') as f:
            f.write("Some text")

def create_boundary_ages(young_file, old_file, target_age, age_diff):
    now = datetime.now()
    target_time = now-target_age
    young_time = target_time + age_diff
    old_time = target_time - age_diff

    young_timestamp = young_time.timestamp()
    old_timestamp = old_time.timestamp()

    os.utime(young_file, (young_timestamp,young_timestamp))
    os.utime(old_file, (old_timestamp,old_timestamp))

#Test RemovalCriteria
def test_last_modified_age(tmp_path):
    d = tmp_path / "last_modified"
    d.mkdir()

    os.chdir(d)

    files = ["new.txt", "less_than_a_week.txt", "more_than_a_week.txt", "old.txt"]

    # Make new files
    for filename in files:
        with open(filename,'w') as f:
            f.write("Some text")

    age=timedelta(weeks=1)
    
    # Give less_than_a_week.txt and more_than_a_week.txt appropriate ages
    create_boundary_ages("less_than_a_week.txt","more_than_a_week.txt", age, timedelta(minutes=1))

    # Give old.txt old modified time (1970-01-01 00:00 UTC)
    os.utime("old.txt", (0,0))

    rc = RemovalCriteria().set_max_age(age,age_parameter="last_modified")

    files = rc.get_candidates(os.getcwd())

    assert len(files) == 2
    assert str(d / "new.txt") not in files
    assert str(d / "less_than_a_week.txt") not in files
    assert str(d / "more_than_a_week.txt") in files
    assert str(d / "old.txt") in files


def test_last_accessed_age(tmp_path):
    d = tmp_path / "last_modified"
    d.mkdir()

    os.chdir(d)

    files = ["new.txt", "less_than_a_week.txt", "more_than_a_week.txt", "old.txt"]

    # Make new files
    for filename in files:
        with open(filename,'w') as f:
            f.write("Some text")

    age=timedelta(weeks=1)
    
    # Give less_than_a_week.txt and more_than_a_week.txt appropriate ages
    create_boundary_ages("less_than_a_week.txt","more_than_a_week.txt", age, timedelta(minutes=1))

    # Give old.txt old modified time (1970-01-01 00:00 UTC)
    
    os.utime("old.txt", (0,0))

    rc = RemovalCriteria().set_max_age(age,age_parameter="last_accessed")

    files = rc.get_candidates(os.getcwd())

    assert len(files) == 2
    assert str(d / "new.txt") not in files
    assert str(d / "less_than_a_week.txt") not in files
    assert str(d / "more_than_a_week.txt") in files
    assert str(d / "old.txt") in files

def test_created_age(tmp_path):
    pass