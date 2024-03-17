from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from Finhub import db
from .models import Profile, Application, Bursary, User
import os
from datetime import datetime


views = Blueprint('views', __name__)


def is_admin():
    logged_user = User.query.get(int(current_user.id))
    return logged_user.is_admin


@views.route('/')
def index():
    if current_user.is_authenticated:
        if is_admin() == True:
            return redirect(url_for('admin.admin_dashboard'))
    return render_template("index.html", user=current_user)


@views.route('/bursaries')
@login_required
def bursaries():
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))

    bursary_list = Bursary.query.all()
    bursaries_count = len(bursary_list)
    return render_template("bursaries__list.html", bursaries=bursary_list, user=current_user, bursaries_count=bursaries_count)


@views.route('/bursary-details/<id>')
@login_required
def bursary_details(id):
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))
    bursary = Bursary.query.get_or_404(int(id))
    current_date = datetime.now().date()
    bursary_closing_date = bursary.closing_date.date()
    status = "Bursary Valid"

    if bursary_closing_date < current_date:
        flash("This bursary is expired!", category='error')
        status = "Bursary Expired"

    return render_template("bursary__details.html", user=current_user, details=bursary, status=status)


@views.route('/submit-application/<ref>', methods=['GET', 'POST'])
@login_required
def submit_application(ref):
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))
    bursary = Bursary.query.filter_by(reference_number=ref).first()

    current_date = datetime.now().date()
    bursary_closing_date = bursary.closing_date.date()

    if bursary_closing_date < current_date:
        flash("Application for this bursary are not allowed", category='error')
        return redirect('/bursaries')

    matric = ''
    academic = ''
    identity = ''
    affidavit = ''

    if request.method == "POST":
        if bursary.matric_required:
            matric = request.files['matric_certificate']
        if bursary.academic_required:
            academic = request.files['academic_transcript']
        if bursary.certified_id_required:
            identity = request.files['id_copy']
        if bursary.unemployment_affidavit:
            affidavit = request.files['affidavit']

        already_applied = Application.query.filter_by(
            app_reference_number=bursary.reference_number, user_id=current_user.id)

        if already_applied.count() > 0:
            flash("You have already applied for this bursary", category='error')
            return redirect('/bursaries')

        if matric:
            matric_name = secure_filename('Matric_Certificate.pdf')
        else:
            matric_name = "Not Available"
        if academic:
            academic_name = secure_filename('Academic_Transcript.pdf')
        else:
            academic_name = "Not Available"
        if identity:
            identity_name = secure_filename('Identity_Document.pdf')
        else:
            identity_name = "Not Available"
        if affidavit:
            affidavit_name = secure_filename('Affidavit.pdf')
        else:
            affidavit_name = "Not Available"

        cover_letter = request.form.get('cover_letter')

        profile = Profile.query.filter_by(user_id=current_user.id).first()

        if not os.path.exists('Finhub/static/uploads'):
            os.mkdir('Finhub/static/uploads')

        path = profile.student_number + ' Docs'
        uploads_path = 'Finhub/static/uploads/'

        if not os.path.exists(uploads_path + '/' + path):
            os.mkdir(uploads_path + '/' + path)

        if not os.path.exists(uploads_path + '/' + path + '/' + ref):
            os.mkdir(uploads_path + '/' + path + '/' + ref)

        applicant_docs_path = uploads_path + '/' + path + '/' + ref + '/'

        # Save Matric Certificate
        if matric:
            matric.save(applicant_docs_path + matric_name)
        # Save Academic Transcript
        if academic:
            academic.save(applicant_docs_path + academic_name)
        # Save Identity Documet
        if identity:
            identity.save(applicant_docs_path + identity_name)
        # save Affidavit
        if affidavit:
            affidavit.save(applicant_docs_path + affidavit_name)

        new_application = Application(
            user_id=current_user.id,
            id_document=identity_name,
            matric_certificate=matric_name,
            academic_transcript=academic_name,
            cover_letter=cover_letter,
            unemployed_affidavit=affidavit_name,
            app_reference_number=ref,
            application_status="Submitted",
            is_submitted=True
        )

        bursary.number_of_applicants += 1

        db.session.add(new_application)
        db.session.commit()

        flash("Application Submitted Successfully!", category='success')
        return redirect('/application-success')

    return render_template("apply__for__bursary.html", user=current_user, bursary=bursary)


@views.route('/application-success')
@login_required
def application_success():
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))
    return render_template("application__success.html", user=current_user)


@views.route('/my-applications')
@login_required
def my_applications():
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))
    return render_template("my__aplications.html", user=current_user)


@views.route('/application-tracking/<id>')
@login_required
def track_application(id):
    if is_admin() == True:
        return redirect(url_for('admin.admin_dashboard'))

    application_details = Application.query.get_or_404(int(id))
    bursary = Bursary.query.filter_by(
        reference_number=application_details.app_reference_number).first()
    if application_details.user_id != current_user.id:
        flash("Access Denied! You can't track other user's applications",
              category='error')
        return redirect('/my-applications')
    return render_template("application__tracking.html", user=current_user, application=application_details, bursary=bursary)
