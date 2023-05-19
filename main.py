from urllib import response
from flask import Flask, request, render_template, url_for, redirect
import os
from time import time

app = Flask(__name__, static_folder="")


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def root_dir():
    return subdir("")

@app.route("/get/")
def root_dir1():
    return subdir("")

def file_menu(file_path : str):
    # keys = dict()
    # keys.filename = os.path.split(file_path)[-1]
    # some info about file
    # 
    return "in progress..."

def get_type(path:str, name:str):
    full_path = os.path.join(path, name)
    return "dir" if os.path.isdir(full_path) else "file" if os.path.isfile(full_path) else "link" if os.path.islink(full_path) else "?"

@app.route("/get/<path:subpath>")
def subdir(subpath : str):
    print("!!!!!!!!!!!!", "/"+subpath)
    realpath = "/" + subpath
    if (os.path.isfile("/"+subpath)):
        return file_menu("/"+subpath)
    if (os.path.isdir("/"+subpath)):
        subdirs = []
        for i in os.listdir("/"+subpath.strip()):
            i_path = os.path.join(realpath, i)
            i_params = dict()
            i_params["name"] = i
            i_params["size"] = 0
            if (os.path.islink(i_path)):
                i_params["type_icon"] = "/static/link.png"
                i_params["type"] = "link"
            elif (os.path.isdir(i_path)):
                i_params["type_icon"] = "/static/folder.png"
                i_params["type"] = "directory"
            elif (os.path.isfile(i_path)):
                i_params["type_icon"] = "/static/paper.png"
                i_params["type"] = "file"
            else:
                i_params["type_icon"] = "/static/question.png"
                i_params["type"] = "undefined type"
            i_params["href_path"] = "/get" + i_path
            print(os.path.getmtime(i_path))
            subdirs.append(i_params)
        print(subpath)
        print(os.path.split(subpath))
        print("yay")
        print("kek", "/get/" + (os.path.split(subpath)[0] if subpath.strip() else ""))
        return render_template("index.html", curdir="/"+subpath.strip(), subdirs=subdirs, up_dir="/get/" + (os.path.split(subpath)[0] if subpath.strip() else ""))


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0