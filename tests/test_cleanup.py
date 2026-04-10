import junky.cleanup
from junky.config import RemovalCriteria
from datetime import datetime, timedelta
import io
import os
import sys

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
    

# junky.cleanup.clean_cwd tests

def test_empty_dir_clean_cwd(capsys,tmp_path):
    d = tmp_path / "empty_dir_clean_cwd"
    d.mkdir()
    os.chdir(d)
    junky.cleanup.clean_cwd()

    captured = capsys.readouterr()

    assert captured.out == "No files to delete.\n"

def test_only_new_clean_cwd(capsys,tmp_path):
    d = tmp_path / "only_new_clean_cwd"
    d.mkdir()

    os.chdir(d)

    # Make new files
    with open("file1.txt",'w') as f:
        f.write("Some text")
    with open("file2.txt",'w') as f:
        f.write("Some other text")

    junky.cleanup.clean_cwd()

    captured = capsys.readouterr()

    assert captured.out == "No files to delete.\n"
    
    files = os.listdir()

    assert "file1.txt" in files
    assert "file2.txt" in files

def test_week_old_clean_cwd(capsys,tmp_path,monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("y\n"))

    d = tmp_path / "week_old_clean_cwd"
    d.mkdir()

    os.chdir(d)

    files = ["new.txt", "less_than_a_week.txt", "more_than_a_week.txt", "old.txt"]

    # Make new files
    for filename in files:
        with open(filename,'w') as f:
            f.write("Some text")
    
    # Give less_than_a_week.txt and more_than_a_week.txt appropriate ages
    create_boundary_ages("less_than_a_week.txt","more_than_a_week.txt", timedelta(weeks=1), timedelta(minutes=1))

    # Give old.txt old modified time (1970-01-01 00:00 UTC)
    os.utime("old.txt", (0,0))

    junky.cleanup.clean_cwd()

    captured = capsys.readouterr()

    assert captured.out == f"Found 2 stale files in {os.getcwd()}.\nAre you sure you want to delete? (Y/n) "

    files = os.listdir()

    assert len(files) == 2
    assert "new.txt" in files
    assert "less_than_a_week.txt" in files
    assert "more_than_a_week.txt" not in files
    assert "old.txt" not in files

# remove_files tests
def test_week_old(tmp_path):
    d = tmp_path / "week_old"
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

    rc = RemovalCriteria().set_max_age(age)

    junky.cleanup.remove_files(os.getcwd(),rc)

    files = os.listdir()

    assert len(files) == 2
    assert "new.txt" in files
    assert "less_than_a_week.txt" in files
    assert "more_than_a_week.txt" not in files
    assert "old.txt" not in files

def test_day_old(tmp_path):
    d = tmp_path / "day_old"
    d.mkdir()

    os.chdir(d)

    files = ["new.txt", "less_than_a_day.txt", "more_than_a_day.txt", "old.txt"]

    # Make new files
    for filename in files:
        with open(filename,'w') as f:
            f.write("Some text")

    age=timedelta(days=1)
    
    # Give less_than_a_day.txt and more_than_a_day.txt appropriate ages
    create_boundary_ages("less_than_a_day.txt","more_than_a_day.txt", age, timedelta(minutes=1))

    # Give old.txt old modified time (1970-01-01 00:00 UTC)
    os.utime("old.txt", (0,0))

    rc = RemovalCriteria().set_max_age(age)

    junky.cleanup.remove_files(os.getcwd(),rc)

    files = os.listdir()

    assert len(files) == 2
    assert "new.txt" in files
    assert "less_than_a_day.txt" in files
    assert "more_than_a_day.txt" not in files
    assert "old.txt" not in files

def test_remove_dir(tmp_path):
    d = tmp_path / "remove_dir"
    d.mkdir()

    os.chdir(d)

    sub_d = d / "test_dir"
    sub_d.mkdir()

    not_empty_d = d / "not_empty"
    not_empty_d.mkdir()

    create_dummy_files(["test.txt","not_empty/test.txt"])

    os.utime("test_dir",(0,0))
    os.utime("not_empty",(0,0))
    os.utime("test.txt",(0,0))

    rc = RemovalCriteria().set_max_age(timedelta(seconds=1))

    rc.ignore_dirs = False
    rc.ignore_files = True

    junky.cleanup.remove_files(os.getcwd(),rc)

    files = os.listdir()

    assert len(files) == 1
    assert "test.txt" in files
    assert "test_dir" not in files
    assert "not_empty" not in files

def test_abort(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("n\n"))
    
    d = tmp_path / "test_abort"
    d.mkdir()

    os.chdir(d)

    create_dummy_files(["file.txt"])

    os.utime("file.txt",(0,0))

    rc = RemovalCriteria().set_max_age(timedelta(seconds=1))
    junky.cleanup.remove_files(os.getcwd(),rc,require_confirmation=True)

    captured = capsys.readouterr()

    assert captured.out == "Are you sure you want to delete? (Y/n) Aborted file deletion.\n", "Output text does not match"
    
    files = os.listdir()

    assert len(files) == 1
    assert "file.txt" in files

def test_invalid_input(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("invalid\nyesterday\nno, not valid\nnO"))
    
    d = tmp_path / "test_abort"
    d.mkdir()

    os.chdir(d)

    create_dummy_files(["file.txt"])

    os.utime("file.txt",(0,0))

    rc = RemovalCriteria().set_max_age(timedelta(seconds=1))

    junky.cleanup.remove_files(os.getcwd(),rc,require_confirmation=True)

    captured = capsys.readouterr()

    assert captured.out == ("Are you sure you want to delete? (Y/n) Invalid input\n"*3 + "Are you sure you want to delete? (Y/n) Aborted file deletion.\n"), "Output text does not match"
    
    files = os.listdir()

    assert len(files) == 1
    assert "file.txt" in files