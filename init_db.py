from app import create_app
from extensions import db
from werkzeug.security import generate_password_hash
from config import Config

app = create_app()
app.config.from_object(Config)

with app.app_context():
    # Import models after app context is created
    from models import Admin
    
    # Clean reset database
    db.drop_all()
    db.create_all()  # This creates tables with the latest schema
    
    # Check if admin exists
    admin = Admin.query.filter_by(username='admin').first()
    
    if not admin:
        new_admin = Admin(
            username='admin',
            password=generate_password_hash('your-new-password-here')
            # home_title and home_subtitle will use default values
        )
        db.session.add(new_admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists") 