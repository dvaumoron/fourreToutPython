
from pathlib import Path
from shutil import copy, rmtree
from spider import *

dir_path = Path("exemple/lib")
archive_path = Path("exemple/archive.zip")

@task
def clean():
    "Erase lib folder and archive.zip ."

    print("cleaning...")
    rmtree(dir_path, ignore_errors=True)
    try:
        archive_path.unlink()
    except FileNotFoundError:
        pass

@task(need="compile")
def test():
    "Trully do nothing."

    print("testing...")

@task()
def download():
    dir_path.mkdir(parents=True, exist_ok=True)

    file_list = ("http://localhost/index.html",
                 "http://localhost/main.css")

    download_list(dir_path, file_list)

    test_path = dir_path / "test"
    test_path.mkdir(parents=True, exist_ok=True)

    print("copy exemple/toto.txt to exemple/lib/test/toto.txt")

    toto_file = Path("exemple/toto.txt")
    copy(toto_file, test_path)

@task(name="compile", need="download")
def mycompile():
    print("compiling...")

@task(need="test")
def archive():
    to_zip(archive_path, dir_path, dir_path.rglob("*.*"))

@task(need="archive")
def deploy():
    print("deploying...")

@task(need=("test", "deploy"))
def start():
    print("starting...")

if __name__ == "__main__":
    main("0.7", "test spider task runner")
