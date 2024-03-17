from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Profile
from werkzeug.security import check_password_hash, generate_password_hash
from Finhub import db
from flask_login import login_user, logout_user, current_user, login_required
import datetime
import random

auth = Blueprint('auth', __name__)


def is_admin():
    logged_user = User.query.get(int(current_user.id))
    return logged_user.is_admin


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Sucessfully logged in", category='success')
                if user.is_admin:
                    return redirect(url_for('admin.admin_dashboard'))
                return redirect(url_for('views.index'))
            else:
                flash("Authentication Failed!", category='error')
        else:
            flash("This user is not registered", category='error')

    return render_template("login.html", user=current_user)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if is_admin() == True:
            return redirect(url_for('admin.admin_dashboard'))
    if request.method == "POST":
        first_name = request.form.get('firstname')
        last_name = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('cpassword')

        user = User.query.filter_by(email=email).first()

        if user:
            flash("User already exist", category='error')

        elif len(first_name) < 4 or len(last_name) < 4:
            flash(
                "First and last name must be at least 4 or more charecters long",
                category='error'
            )
        elif password != confirm_password:
            flash("Password does'nt match with confirm password", category='error')
        else:
            # register account
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(
                    password, method='pbkdf2:sha256'),
            )

            db.session.add(new_user)
            db.session.commit()

            student_number = generate_student_number(first_name, last_name)

            new_profile = Profile(user_id=new_user.id,
                                  student_number=student_number)
            db.session.add(new_profile)
            db.session.commit()

            # login_user(user, remember=True)

            flash("Your account was successfully created", category='success')
            return redirect(url_for('auth.login'))

    return render_template("register.html", user=current_user)


@auth.route('/sign-out')
@login_required
def sign_out():
    logout_user()
    flash("Signed out successfully", category='error')
    return redirect(url_for('auth.login'))


@auth.route('/profile')
@login_required
def profile():
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    return render_template('user__profile.html', user_profile=user_profile, user=current_user)


def generate_student_number(first_name, last_name):
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month
    first_name_length = len(first_name)
    last_name_length = len(last_name)
    random_number = random.randint(1, 9)
    student_no = str(current_year) + str(current_month) + \
        str(first_name_length) + str(last_name_length) + str(random_number)
    return student_no


@login_required
@auth.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))
    id = current_user.id
    if request.method == "POST":
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

    user = User.query.get(int(id))
    if user:
        if check_password_hash(user.password, current_password):
            user.password = generate_password_hash(
                new_password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Password updated', category='success')
        else:
            flash('Current password is incorrect', category='error')

    return redirect(url_for('auth.profile'))


@auth.route('/update-user-details', methods=['GET', 'POST'])
@login_required
def update_user_details():
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))
    user_profile = Profile.query.filter_by(user_id=current_user.id).first()
    user = User.query.get(int(current_user.id))

    if request.method == "POST":
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        birth_date = request.form.get('birth_date')
        gender = request.form.get('gender')
        address = request.form.get('address')

        user.first_name = first_name
        user.last_name = last_name
        if birth_date:
            user_profile.date_of_birth = birth_date
        else:
            user_profile.date_of_birth = None
        user_profile.gender = gender
        user_profile.address = address

        db.session.commit()

        flash("User details updated successfully", category='success')
        return redirect(request.url)

    return render_template("manage__profile.html", user=current_user, user_profile=user_profile)
