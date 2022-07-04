from datetime import datetime
import os
import sys
from time import sleep

from flask import Blueprint, flash, render_template, redirect, \
    url_for, request, session
from bson.objectid import ObjectId

from models import Project
from models import User


from runit import RunIt

EXTENSIONS = {'python': '.py', 'python3': '.py', 'php': '.php', 'javascript': '.js'}
LANGUAGE_ICONS = {'python': 'python', 'python3': 'python', 'php': 'php',
                  'javascript': 'node-js', 'typescript': 'node-js'}

project = Blueprint('project', __name__, url_prefix='/projects', static_folder=os.path.join('..','static'))

@project.before_request
def authorize():
    if not 'user_id' in session:
        return redirect(url_for('public.index'))

@project.get('/')
def index():
    user_id = session['user_id']
    projects = Project.get_by_user(user_id)
    return render_template('projects/index.html', page='projects',\
            projects=projects)

@project.post('/')
def new_project():
    user_id = session['user_id']
    name = request.form.get('name')
    date = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")
    if name:
        Project(name, user_id).save()
        flash('Project created successfully', category='success')
    else:
        flash('Name of the project is required', category='danger')
    return redirect(url_for('project.projects'))

@project.patch('/')
def update_project():
    user_id = session['user_id']
    return render_template('projects/index.html', page='projects', projects=[])

@project.delete('/')
def delete_project():
    user_id = session['user_id']
    return render_template('projects/index.html', page='projects', projects=[])
