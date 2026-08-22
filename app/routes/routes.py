from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

# Create a Blueprint named 'auth'
auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # If the user submits the form
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if a user with this email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists. Please log in.')
            return redirect(url_for('auth.signup'))

        # Create new user and hash the password
        new_user = User(email=email, username=username)
        new_user.set_password(password)

        # Add to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.')
        return redirect(url_for('auth.login'))

    # If it's a GET request, just show the signup page
    return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user by email
        user = User.query.filter_by(email=email).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('auth.dashboard')) # Redirect to their trips
        else:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# A protected test route to verify it works
@auth.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}! Welcome to Globe Trotter.'