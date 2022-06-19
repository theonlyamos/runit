from flask import Blueprint, redirect, render_template, \
     request, session, url_for, flash

from common.security import authenticate
from models import User

public = Blueprint('public', __name__)

'''
@public.before_request
def initial():
    os.chdir(os.getenv('RUNIT_HOMEDIR'))
''' 

@public.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('account.index'))
    return render_template('login.html')

@public.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        c_password = request.form.get('cpassword')
        if password != c_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        user = User.get_by_email(email)
        if user:
            flash('User is already Registered!', 'danger')
            return render_template('register.html')
        
        user = User(email, name, password).save()
        flash('Registration Successful!', 'success')
        return redirect(url_for('public.index'))

    return render_template('register.html')

@public.post('/login/')
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = authenticate(email, password)
    if user:
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        return redirect(url_for('account.index'))
    else:
        flash('Invalid Login Credentials', 'danger')
    return redirect(url_for('public.index'))



'''
@public.route('/<account>/', methods=['GET','POST','PUT','PATCH','DELETE'])
def main(account):
    if (os.path.isdir(os.path.join('accounts', account))):
        result = RunIt.start(account)
        return result
    else:
        return RunIt.notfound()

@public.route('/<account>/<page>/', methods=['GET','POST','PUT','PATCH','DELETE'])
def page(account, page='index'):
    if (os.path.isdir(os.path.join('accounts', account))):
        result = RunIt.start(account, page)
        #os.chdir(os.path.join('..', '..'))
        return result
    else:
        return RunIt.notfound()
'''