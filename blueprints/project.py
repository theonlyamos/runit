from flask import Blueprint, render_template, redirect, \
    url_for, request, session, flash
from bson.objectid import ObjectId
from models.project import Project

from datetime import datetime
import os

project = Blueprint('project', __name__, 
            static_folder=os.path.join('..','static'))

@project.before_request
def authorize():
    if not 'user_id' in session:
        return redirect(url_for('public.index'))

@project.route('/', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def projects():
    user_id = session['user_id']
    if request.method == 'GET':
        projects = Project.get_by_user(user_id)
        return render_template('projects/index.html', page='projects',\
             projects=projects)

    elif request.method == 'POST':
        name = request.form.get('name')
        date = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")
        if name:
            Project(name, user_id).save()
            flash('Project created successfully', category='success')
        else:
            flash('Name of the project is required', category='danger')
        return redirect(url_for('account.projects'))
    
    elif request.method == 'PATCH':
        return render_template('projects/index.html', page='projects', projects=[])
    elif request.method == 'DELETE':
        return render_template('projects/index.html', page='projects', projects=[])