from app import create_app
from models import db
from sqlalchemy import inspect

app = create_app()
app.app_context().push()

inspector = inspect(db.engine)
columns = inspector.get_columns('admin')

print("Admin Table Columns:")
for col in columns:
    print(f"- {col['name']} ({col['type']})") 