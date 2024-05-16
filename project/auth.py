from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, login_required, logout_user
from sqlalchemy import text
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    #test
    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password and compare it with the stored password
    if user and check_password_hash(user.password, password):
        # If the check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))
    else:
        # If the user doesn't exist or the password is wrong, reload the page
        flash('Please check your login details and try again.')
        current_app.logger.warning("User login failed")
        return redirect(url_for('auth.login'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    sql_query = text('select * from user where email = :email')
    user = db.session.execute(sql_query, {'email': email}).all()
    if len(user) > 0: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')  # 'flash' function stores a message accessible in the template code.
        current_app.logger.debug("User email already exists")
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. TODO: Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2', salt_length=16))
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user();
    return redirect(url_for('main.index'))

# See https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login for more information
