from datetime import datetime
import os
from sys import prefix

from flask import Blueprint, flash, render_template, redirect, \
    url_for, request, session
from bson.objectid import ObjectId

from models import Project
from models import User
from common import Database
from models.function import Function


from runit import RunIt

EXTENSIONS = {'python': '.py', 'python3': '.py', 'php': '.php', 'javascript': '.js'}
LANGUAGE_ICONS = {'python': 'python', 'python3': 'python', 'php': 'php',
                  'javascript': 'node-js', 'typescript': 'node-js'}

admin = Blueprint('admin', __name__, subdomain='admin', static_folder=os.path.join('..','static'))

@admin.before_request
def authorize():
    if not 'user_id' in session:
        return redirect(url_for('public.index'))

@admin.route('/')
def index():
    user = User.get(session['user_id'])
    return render_template('admin/home.html', page='home', user=user)

@admin.route('/projects/', methods=['GET', 'POST', 'PATCH', 'DELETE'])
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
        return redirect(url_for('admin.projects'))
    
    elif request.method == 'PATCH':
        return render_template('projects/index.html', page='projects', projects=[])
    elif request.method == 'DELETE':
        return render_template('projects/index.html', page='projects', projects=[])

@admin.route('/functions/', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def functions():
    global EXTENSIONS
    global LANGUAGE_ICONS

    if request.method == 'GET':
        functions = Function.get_by_user(session['user_id'])
        projects = Project.get_by_user(session['user_id'])
        
        return render_template('functions/index.html', page='functions',\
                functions=functions, projects=projects,\
                languages=EXTENSIONS, icons=LANGUAGE_ICONS)

    elif request.method == 'POST':
        name = request.form.get('name')
        project_id = request.form.get('project_id')
        language = request.form.get('language')
        description = request.form.get('description')
        date = (datetime.utcnow()).strftime("%a %b %d %Y %H:%M:%S")

        if name and language:
            data = {'name': name, 'user_id': ObjectId(session['user_id']),\
                    'filename': name+EXTENSIONS[language],\
                    'project_id': ObjectId(project_id), \
                    'language': language, 'description': description,\
                    'created_at': date, 'updated_at': date}

            Database.db.functions.insert_one(data)
            flash('Function created successfully', category='success')
        else:
            flash('Error: Name and Language fields are required!', category='danger')
        return redirect(url_for('admin.functions'))

@admin.route('/profile/')
def profile():
    return render_template('admin/profile.html', page='profile')

@admin.route('/logout/')
def logout():
    del session['user_id']
    return redirect(url_for('public.index'))

@admin.route('/<page>')
def main(page):
    if (os.path.isdir(os.path.join('admins', page))):
        os.chdir(os.path.join('admins', page))
        result = RunIt.start()
        #os.chdir(os.path.join('..', '..'))
        return result
    else:
        return RunIt.notfound()