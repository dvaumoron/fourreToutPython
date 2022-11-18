
from argparse import ArgumentParser
from io import TextIOWrapper
from shutil import copyfileobj
from urllib.error import HTTPError
from urllib.request import urlopen
from zipfile import ZipFile, ZIP_DEFLATED

__all__ = ("task", "main", "download_list", "to_zip")

tasks_dict = {}
reserved_task_names = {"all", "list"}

class Task:
    __slots__ = ("name", "need", "action", "recursive_call")
    def __init__(self, name, need, action):
        if name in reserved_task_names:
            raise SyntaxError(f"'{name}' is not allowed as task name")
        if name in tasks_dict:
            raise SyntaxError(f"task with name '{name}' already exist")
        self.name = name
        self.need = need
        self.action = action
        self.recursive_call = False
        tasks_dict[name] = self
    def run(self, runned_tasks):
        for previous in self.need:
            if previous not in runned_tasks:
                tasks_dict[previous].run(runned_tasks)
        name = self.name
        print(name, end=":\n")
        self.action()
        runned_tasks.add(name)
    def test_loop(self, runned_tasks):
        if self.recursive_call:
            raise SyntaxError(f"loop in task dependencies of {self.name}")
        try:
            self.recursive_call = True
            for previous in self.need:
                if previous not in runned_tasks:
                    tasks_dict[previous].test_loop(runned_tasks)
            runned_tasks.add(self.name)     
        finally:
            self.recursive_call = False
    def display(self, runned_tasks):
        need = self.need
        for previous in need:
            if previous not in runned_tasks:
                tasks_dict[previous].display(runned_tasks)
        name = self.name
        print(name)
        if need:
            print("\tdepends on :", ", ".join(need))    
        doc = self.action.__doc__
        if doc:
            print("\t", doc, sep="")
        runned_tasks.add(name)
    def __repr__(self):
        return f"Task({self.name!r}, need={self.need!r}, action={self.action!r})"

def task(func=None, *, name=None, need=()):
    "Decorator to transform a zero argument function in Task."

    if isinstance(need, str):
        need = need,
    else:
        need = tuple(need)

    def create_task(func):
        nonlocal name
        if name is None:
            name = func.__name__
        return Task(name, need, func)

    if func is None:
        return create_task
    return create_task(func)

def on_all_task(func):
    runned_tasks = set()
    for t in tasks_dict.values():
        if t.name not in runned_tasks:
            func(t, runned_tasks)

def main(version, description=None):
    try:
        on_all_task(Task.test_loop)

        parser = ArgumentParser(description=description)
        parser.add_argument("-sv", "--spiderversion", action="version",
                            version="spider version 0.15",
                            help="show spider's version number and exit")
        parser.add_argument("-v", "--version", action="version",
                            version=f"%(prog)s version {version}")
        parser.add_argument("target", nargs="?", default="all",
                            help="target task name (default: all)")

        target = parser.parse_args().target

        if target == "all":
            on_all_task(Task.run)
        elif target == "list":
            on_all_task(Task.display)
        else:
            tasks_dict[target].run(set())
    except KeyError as ke:
        print("task not found :", ke)

def extract_name(link):
    i = 0
    while True:
        j = link.find("/", i)
        if j == -1:
            break
        else:
            i = j + 1
    return link[i:]

def print_depth(depth):
    print("\t" * depth, end="")

def download_list(dir_path, links, depth=0):
    for link in links:
        link = link.strip(" \n")
        if len(link) > 0 and link[0] != "#":
            name = extract_name(link)
            p = dir_path / name
            print_depth(depth)
            if p.exists():
                print(name, "exists")
            else:
                print("downloading", name)
                with urlopen(link) as src, open(p, "wb") as dest:
                    copyfileobj(src, dest)
                try:
                    with TextIOWrapper(urlopen(link + ".dep")) as dep:
                        download_list(dir_path, dep, depth + 1)
                except HTTPError:
                    print_depth(depth)
                    print("no dependencies for", name)

def to_zip(zip_path, parent_path, files):
    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED, compresslevel=9) as zf:
        for file_path in files:
            target_path = str(file_path.relative_to(parent_path))
            print(f"adding {file_path} to {zip_path} at {target_path}")
            with open(file_path, "rb") as src, zf.open(target_path, "w") as dest:
                copyfileobj(src, dest)
