from datetime import datetime
import os
from sys import prefix

from flask import Blueprint, flash, render_template, redirect, \
    url_for, request, session
from bson.objectid import ObjectId

from models import User
from models import Project
from models import Admin
from common import Database
from common import Utils
from models.function import Function


from runit import RunIt

EXTENSIONS = {'python': '.py', 'python3': '.py', 'php': '.php', 'javascript': '.js'}
LANGUAGE_ICONS = {'python': 'python', 'python3': 'python', 'php': 'php',
                  'javascript': 'node-js', 'typescript': 'node-js'}

admin = Blueprint('admin', __name__, subdomain='admin', static_folder=os.path.join('..','static'))

@admin.get('/login/')
def loginpage():
    return render_template('admin/login.html', title='Login')

# @admin.before_request
# def authorize():
#     if not 'admin_id' in session:
#         return redirect(url_for('admin.loginpage'))

@admin.route('/')
def index():
    if not 'admin_id' in session:
        return redirect(url_for('admin.loginpage'))
    
    admin = Admin.get(session['admin_id'])
    return render_template('admin/index.html', page='home', admin=admin)

@admin.post('/login/')
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    admin = Admin.get_by_username(username)
    #print(admin)
    if admin:
        if (Utils.check_hashed_password(password, admin.password)):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.name
            session['admin_username'] = admin.username
            return redirect(url_for('admin.index'))
    flash('Invalid Login Credentials', 'danger')
    return redirect(url_for('admin.loginpage'))

@admin.get('/users/')
def users():
    users = User.all()
    view = request.args.get('view')
    view = view if view else 'grid'

    return render_template('admin/users/index.html', page='users',\
            users=users, view=view, icons=LANGUAGE_ICONS)

@admin.get('/users/<string:user_id>')
@admin.get('/users/<string:user_id>/')
def user(user_id):
    try:
        user = User.get(user_id)
        projects = Project.get_by_user(user.id)
        
        view = request.args.get('view')
        view = view if view else 'grid'
        
        return render_template('admin/users/details.html', page='users',\
            user=user.json(), projects=projects, view=view, icons=LANGUAGE_ICONS)
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('admin.users'))

@admin.get('/projects/')
def projects():
    projects = Project.all()
    return render_template('admin/projects/index.html', page='projects',\
            projects=projects)

@admin.route('/functions/', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def functions():
    global EXTENSIONS
    global LANGUAGE_ICONS

    if request.method == 'GET':
        functions = Function.get_by_admin(session['admin_id'])
        projects = Project.get_by_admin(session['admin_id'])
        
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
            data = {'name': name, 'admin_id': ObjectId(session['admin_id']),\
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
    del session['admin_id']
    return redirect(url_for('admin.loginpage'))

@admin.route('/<page>')
def main(page):
    if (os.path.isdir(os.path.join('admins', page))):
        os.chdir(os.path.join('admins', page))
        result = RunIt.start()
        #os.chdir(os.path.join('..', '..'))
        return result
    else:
        return RunIt.notfound()