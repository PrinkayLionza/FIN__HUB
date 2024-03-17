from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from werkzeug.utils import secure_filename
from Finhub import db
from .models import Bursary, Application, User, Profile
import random
import os
from datetime import datetime
import time
from functools import wraps
from flask_login import current_user

admin = Blueprint('admin', __name__)


# admin decorator

def is_adminnistrator():
    logged_user = User.query.get(int(current_user.id))
    return logged_user.is_admin

# Get Date From a string Function


def get_date_from_string(date_str):
    try:
        date = datetime.strptime(date_str, "%m/%d/%Y")
    except TypeError:
        date = datetime.datetime(
            *(time.strptime(date_str, "%m/%d/%Y")[0:6]))
    return date


@admin.route('/unauthorized-access')
def unauthorised():
    return render_template('admin/unauthoused__access.html', user=current_user)


@admin.route('/admin')
@login_required
def admin_dashboard():
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')

    users_count = len(User.query.all())
    apps_count = len(Application.query.filter_by(
        is_successful=False, is_rejected=False).all())
    bursary_count = len(Bursary.query.all())

    apps_success__count = len(
        Application.query.filter_by(is_successful=True).all())
    apps_rejected__count = len(
        Application.query.filter_by(is_rejected=True).all())

    return render_template(
        "admin/admin__dashboard.html",
        users_count=users_count,
        apps_count=apps_count,
        bursary_count=bursary_count,
        apps_rejected_count=apps_rejected__count,
        apps_success_count=apps_success__count
    )

# User


@admin.route('/finhub/users')
@login_required
def finhub_users():
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    users = User.query.all()
    return render_template("admin/finhub__users.html", users=users)

# User Details


@admin.route('/finhub/users/details/<id>')
@login_required
def user_details(id):
    if is_adminnistrator == False:
        return redirect('/unauthorized-access')
    user = User.query.get(int(id))
    profile = Profile.query.filter_by(user_id=user.id).first()
    return render_template("admin/funhub__user__details.html", user=user, profile=profile)

# Manage bursaries


@admin.route('/manage-bursaries')
@login_required
def manage_bursaries():
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    bursaries_list = Bursary.query.all()
    return render_template(
        "admin/bursaries__list.html",
        bursaries_list=bursaries_list
    )


@admin.route('/manage-applications')
@login_required
def manage_applications():
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    applications_list = Application.query.all()
    return render_template(
        "admin/applications__list.html",
        applications_list=applications_list
    )


@admin.route('/application/details/<id>')
@login_required
def application_details(id):
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    application = Application.query.get(int(id))
    application_user = User.query.get(int(application.user_id))
    bursary = Bursary.query.filter_by(
        reference_number=application.app_reference_number).first()
    application_profile = Profile.query.filter_by(
        user_id=application_user.id).first()
    return render_template(
        "admin/application__details.html",
        application=application,
        application_user=application_user,
        application_profile=application_profile,
        bursary=bursary
    )


@admin.route('/application/details/review-documents/<id>')
@login_required
def review_application_docs(id):
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    application = Application.query.get(int(id))
    application_user = User.query.get(int(application.user_id))
    bursary = Bursary.query.filter_by(
        reference_number=application.app_reference_number).first()
    application_profile = Profile.query.filter_by(
        user_id=application_user.id).first()
    return render_template(
        "admin/review__application__documents.html",
        application=application,
        application_user=application_user,
        bursary=bursary,
        application_profile=application_profile
    )


@admin.route('/confirm-review-application', methods=['GET', 'POST'])
@login_required
def confirm_documents_review():
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    if request.method == "POST":
        application_id = request.form.get('application_id')
        application = Application.query.get(int(application_id))
        application.on_review = True
        application.application_status = "Awaiting For Approval"
        db.session.commit()
        flash("Application Status Updated!", category='success')
        return redirect("/manage-applications")


@admin.route('/application/details/approve-application/<id>',  methods=['GET', 'POST'])
@login_required
def approve__application(id):
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    application = Application.query.get(int(id))
    if request.method == "POST":
        application.is_successful = True
        application.application_status = "Application Successful"
        db.session.commit()

        # Send Successful Email

        flash("Application Status Updated!", category='success')
        return redirect("/manage-applications")
    return render_template("admin/approve__application.html", application=application)


@admin.route('/application/details/reject-application/<id>', methods=['GET', 'POST'])
@login_required
def reject__application(id):
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    application = Application.query.get(int(id))
    if request.method == "POST":
        application.is_rejected = True
        application.application_status = "Application Rejected"
        db.session.commit()

        # Send Rection Email

        flash("Application Status Updated!", category='success')
        return redirect("/manage-applications")
    return render_template("admin/reject__application.html", application=application)


# Bursary Management
# Adding New Bursaries

@admin.route('/new-bursary', methods=['GET', 'POST'])
@login_required
def new_bursary():
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    if request.method == "POST":
        title = request.form.get('title')
        company = request.form.get('company')
        company_logo = request.files['company_logo']
        closing_date = request.form.get('closing_date')
        description = request.form.get('description')
        id_copy = request.form.get('id_copy')
        matric = request.form.get('matric')
        academic = request.form.get('academic')
        affidavit = request.form.get('affidavit')

        closing_date_obj = get_date_from_string(closing_date)

        id_copy = True

        if matric is None:
            matric = False
        else:
            matric = True
        if academic is None:
            academic = False
        else:
            academic = True
        if affidavit is None:
            affidavit = False
        else:
            affidavit = True

        # Upload Company Logo
        company_logo_name = secure_filename(company_logo.filename)

        if not os.path.exists('Finhub/static/uploads/logos'):
            os.mkdir('Finhub/static/uploads/logos')
        uploads_path = 'Finhub/static/uploads/logos/'

        if company_logo:
            company_logo.save(uploads_path + company_logo_name)

        reference_number = ""
        initial = 1
        while initial < 6:
            random_number = random.randint(0, 9)
            reference_number += str(random_number)
            initial += 1

        print(reference_number)

        new_bursary = Bursary(
            closing_date=closing_date_obj,
            title=title,
            company=company,
            description=description,
            company_logo=company_logo_name,
            certified_id_required=id_copy,
            matric_required=matric,
            academic_required=academic,
            unemployment_affidavit=affidavit,
            reference_number=reference_number,
            number_of_applicants=0,
            is_valid=True
        )

        db.session.add(new_bursary)
        db.session.commit()
        flash("Bursary Successfully saved", category='success')
        return redirect('/manage-bursaries')

    return render_template("admin/new__bursary.html")

# Deleting Bursary


@admin.route('/delete-bursary/<id>', methods=['GET', 'POST'])
@login_required
def delete_bursary(id):
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    bursary = Bursary.query.get_or_404(int(id))
    if request.method == "POST":
        if bursary:
            db.session.delete(bursary)
            db.session.commit()
            flash("Bursary Record Deleted", category='error')
            return redirect('/manage-bursaries')
    return render_template("admin/delete__bursary.html", bursary=bursary)
# Updating Bursary
# Details


@admin.route('/bursary/details/<id>')
@login_required
def bursary_details(id):
    if is_adminnistrator() == False:
        return redirect('/unauthorized-access')
    bursary = Bursary.query.get_or_404(int(id))
    return render_template("admin/bursary__details.html", bursary=bursary)
