#!/usr/bin/python
import os
import re
import shutil
from optparse import OptionParser

def clean_folder(path, fix=None, exclude=None):
    if not exclude: exclude = []
    if not os.path.exists(path):
        return
    files = os.listdir(path)
    for file in files:
        if file in exclude:
            continue
        rmfile = os.path.join(path, file)
        if os.path.isdir(rmfile):
            shutil.rmtree(rmfile)
        else:
            os.remove(rmfile)
    if fix:
        with open(os.path.join(path, fix), "w") as f:
            f.write("")


def smart_copy(src, target):
    if os.path.isdir(src):
        shutil.copytree(src, target)
    else:
        shutil.copy2(src, target)


def main(top_param, clone):
    if os.path.exists(clone):
        clean_folder(clone, exclude=[".git"])
    if not os.path.exists(clone):
        os.makedirs(clone)

    exclude = [".git"]
    for item in os.listdir(top_param):
        if item in exclude:
            continue
        path = os.path.join(top_param, item)
        smart_copy(path, os.path.join(clone, item))

    folders = [
        "components",
        "node_modules",
        "index/static/css",
        "index/static/js",
        "index/static/img"
    ]
    #remove
    for folder in folders:
        path = os.path.join(clone, folder)
        shutil.rmtree(path)
    folders = [
        "db",
        "media",
        "static"
    ]
    #clean
    for folder in folders:
        clean_folder(os.path.join(clone, folder), ".githolder")

    #move
    project_name = os.path.join(clone, "project_name")
    shutil.move(
        os.path.join(clone, top_param),
        project_name)

    p = re.compile(r"{0}\.".format(top_param))
    files = [
        os.path.join(clone, "manage.py"),
        os.path.join(project_name, "base_settings.py"),
        os.path.join(project_name, "wsgi.py")
    ]
    for path in files:
        f = open(path, "r")
        data = f.read()
        f.close()
        f = open(path, "w")
        data = p.sub('{{project_name}}.', data)
        f.write(data)
        f.close()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-s", "--src", dest="src", help="src", default="visitka")
    parser.add_option("-d", "--dest", dest="dest", help="destination", default="project_name")
    opt, args = parser.parse_args()
    main(opt.src, opt.dest)
