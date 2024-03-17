from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Bursary(db.Model):
    __tablename__ = 'bursaries'

    id = db.Column(db.Integer, primary_key=True)
    closing_date = db.Column(db.DateTime(timezone=True))
    posted_date = db.Column(db.DateTime(timezone=True), default=func.now())
    number_of_applicants = db.Column(db.Integer)
    is_valid = db.Column(db.Boolean, unique=False, default=False)
    reference_number = db.Column(db.String(100), default="")
    title = db.Column(db.String(100), default="")
    company = db.Column(db.String(100), default="")
    description = db.Column(db.String(150), default="")
    certified_id_required = db.Column(db.Boolean, unique=False, default=False)
    matric_required = db.Column(db.Boolean, unique=False, default=False)
    academic_required = db.Column(db.Boolean, unique=False, default=False)
    unemployment_affidavit = db.Column(db.Boolean, unique=False, default=False)
    company_logo = db.Column(db.String(100), default="")


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    applications = db.relationship('Application')
    is_admin = db.Column(db.Boolean, unique=False, default=False)
    created = db.Column(db.DateTime(timezone=True), default=func.now())


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    application_date = db.Column(
        db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    app_reference_number = db.Column(db.String(150))
    id_document = db.Column(db.String(150))
    matric_certificate = db.Column(db.String(150))
    academic_transcript = db.Column(db.String(150))
    unemployed_affidavit = db.Column(db.String(150))
    cover_letter = db.Column(db.String(200))
    application_status = db.Column(db.String(150))
    is_submitted = db.Column(db.Boolean, unique=False, default=False)
    on_review = db.Column(db.Boolean, unique=False, default=False)
    is_successful = db.Column(db.Boolean, unique=False, default=False)
    is_rejected = db.Column(db.Boolean, unique=False, default=False)


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String(10), unique=True)
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.String(100))
    address = db.Column(db.String(100))
    zip_code = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
