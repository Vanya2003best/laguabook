# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from datetime import datetime

from ..models import db, User, Book, VocabularyItem
from ..forms.auth_forms import LoginForm, RegistrationForm, ProfileForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("User already authenticated")
        return redirect(url_for('book.library'))

    form = LoginForm()
    if form.validate_on_submit():
        # Убираем лишние пробелы и приводим имя пользователя к нижнему регистру
        username = form.username.data.strip().lower()
        print(f"Login attempt for: {username}")
        user = User.query.filter(User.username.ilike(form.username.data.strip())).first()
        print(f"User found: {user is not None}")
        print(f"Form data - username: '{form.username.data}', length: {len(form.username.data)}")
        if user is None:
            print("User not found")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        password_check = user.check_password(form.password.data)
        print(f"Password check result: {password_check}")

        if not password_check:
            print("Password incorrect")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        print(f"Next page: {next_page}")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('book.library')
        print(f"Redirecting to: {next_page}")
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    # Clear session data
    if 'chat_session_id' in session:
        del session['chat_session_id']
    if 'chat_history' in session:
        del session['chat_history']
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('book.library'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Приводим имя к нормальному виду
        username = form.username.data.strip().lower()
        user = User(
            username=username,
            email=form.email.data,
            native_language=form.native_language.data,
            learning_language=form.learning_language.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileForm(original_username=current_user.username,
                       original_email=current_user.email)

    if request.method == 'GET':
        # Pre-populate form with user data
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.native_language.data = current_user.native_language
        form.learning_language.data = current_user.learning_language

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.native_language = form.native_language.data
        current_user.learning_language = form.learning_language.data

        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('auth.profile'))

    # Get user stats
    books_count = Book.query.filter_by(user_id=current_user.id).count()
    vocab_count = VocabularyItem.query.filter_by(user_id=current_user.id).count()
    user_stats = {'books': books_count, 'words': vocab_count}

    return render_template('auth/profile.html', title='User Profile',
                           form=form, user_stats=user_stats)