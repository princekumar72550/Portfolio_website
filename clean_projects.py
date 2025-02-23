from app import create_app
from models import Project
from flask_sqlalchemy import SQLAlchemy

app = create_app()
with app.app_context():
    db = SQLAlchemy()
    # Delete all projects with titles 'django' or 'hjhj'
    Project.query.filter(Project.title.in_(['django', 'hjhj'])).delete()
    db.session.commit()
    print("Test projects deleted") 