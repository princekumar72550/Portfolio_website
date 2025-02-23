from flask_dance.contrib.google import make_google_blueprint
from extensions import db
from models import Admin
from flask_login import login_user
import os

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="google_login"
)

def register_google_auth(app):
    app.register_blueprint(google_bp, url_prefix="/google_login")

    @google_bp.route("/google/authorized")
    def google_authorized():
        resp = google_bp.session.get("/oauth2/v2/userinfo")
        if resp.ok:
            user_info = resp.json()
            admin = Admin.query.filter_by(google_id=user_info["id"]).first()
            
            if not admin:
                admin = Admin(
                    username=user_info["email"],
                    google_id=user_info["id"],
                    profile_pic=user_info.get("picture"),
                    email=user_info["email"]
                )
                db.session.add(admin)
                db.session.commit()
            
            login_user(admin)
            return redirect(url_for("admin_dashboard"))
        return "Google login failed" 