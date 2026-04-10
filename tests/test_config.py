from junky.config import Config, RemovalCriteria
from datetime import datetime, timedelta
import os
import time

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

# Test Confifg class
def test_config_read(tmp_path):
    d = tmp_path / "config_read"
    d.mkdir()

    os.chdir(d)

    with open("test.toml",'w') as f:
        f.write("""
            a = "a string"
            b = 4
            
            [subproperty]
            c = "another string"
            d = 8
                
            [subproperty.thing]
            e = "last string"
        """)

    conf = Config().load_from_file("test.toml")

    dic = conf.config

    assert dic["a"] == "a string"
    assert dic["b"] == 4
    assert dic["subproperty"]["c"] == "another string"
    assert dic["subproperty"]["d"] == 8
    assert dic["subproperty"]["thing"]["e"] == "last string"

def test_config_write(tmp_path):
    d = tmp_path / "config_write"
    d.mkdir()

    os.chdir(d)

    conf = Config()

    conf.config = {
        "a": "a string",
        "b": 4,
        "subproperty": {
            "c": "another string",
            "d": 8,
            "thing": {
                "e": "last string"
            },
            "f": "jokes"
        },
        "g": "for real last string"
    }

    conf.write_to_file("test.toml")

    with open("test.toml") as f:
        lines = f.readlines()

    lines_not_empty = [i.rstrip() for i in lines if i.strip() != ""]

    lines_expected = [
        'a = "a string"',
        'b = 4',
        'g = "for real last string"',
        '[subproperty]',
        'c = "another string"',
        'd = 8',
        'f = "jokes"',
        '[subproperty.thing]',
        'e = "last string"'
    ]

    assert len(lines_not_empty) == len(lines_expected)

    for actual, expected in zip(lines_not_empty,lines_expected):
        assert actual == expected

def test_config_get_removal_criteria(tmp_path):
    d = tmp_path / "get_removal_criteria"
    d.mkdir()

    os.chdir(d)

    with open("test.toml",'w') as f:
        f.write("""
            [remove.max_age]
            seconds = 1
            minutes = 2
            hours = 3
            days = 4
            weeks = 5
            
            parameter = "last_accessed"
                
            [remove.ignore]
            files = true
            dirs = false
        """)

    conf = Config().load_from_file("test.toml")

    rc = conf.get_removal_criteria()
    
    assert rc.max_age == timedelta(seconds=1,minutes=2,hours=3,days=4,weeks=5)
    assert rc.max_age_parameter == 'last_accessed'
    assert rc.ignore_files
    assert not rc.ignore_dirs

# Test RemovalCriteria class
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
    d = tmp_path / "last_accessed"
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
    d = tmp_path / "created"
    d.mkdir()

    os.chdir(d)

    # Make new files
    with open("more_than_2_secs.txt",'w') as f:
        f.write("Some text")
    
    time.sleep(2)

    with open("less_than_2_secs.txt",'w') as f:
        f.write("Some text")

    age = timedelta(seconds=2)
    rc = RemovalCriteria().set_max_age(age,age_parameter='created')

    files = rc.get_candidates(os.getcwd())

    assert len(files) == 1
    assert str(d / "less_than_2_secs.txt") not in files
    assert str(d / "more_than_2_secs.txt") in files

        