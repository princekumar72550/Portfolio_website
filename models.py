from flask_login import UserMixin
from extensions import db
from datetime import datetime

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_pic = db.Column(db.String(120))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resume = db.Column(db.String(120))
    home_title = db.Column(db.String(200), default="Welcome to My Portfolio")
    home_subtitle = db.Column(db.String(200), default="Full Stack Developer")
    google_id = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(120), unique=True)
    tokens = db.Column(db.Text)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100))
    skills = db.Column(db.String(200), default='')  # Add default empty string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    proficiency = db.Column(db.Integer)  # 1-100 percentage
    category = db.Column(db.String(50))  # e.g., "Programming", "Design"

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    date_issued = db.Column(db.Date, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    credential_id = db.Column(db.String(50))
    credential_url = db.Column(db.String(200))

    def __repr__(self):
        return f"Certificate('{self.title}', '{self.organization}')"

def load_user(user_id):
    return Admin.query.get(int(user_id)) 