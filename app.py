from flask import Flask, send_from_directory
from extensions import db, login_manager, migrate  # Import from extensions
from google_auth import register_google_auth
import os
from flask_assets import Environment
from whitenoise import WhiteNoise

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='')
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
    app.config.from_pyfile('config.py')
    
    # Add Google OAuth
    app.config['GOOGLE_CLIENT_ID'] = os.getenv("GOOGLE_CLIENT_ID")
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    register_google_auth(app)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'admin_login'

    assets = Environment(app)
    assets.register('main_js', 'js/main.js')
    assets.register('main_css', 'css/main.css')

    with app.app_context():
        # Import inside app context to avoid circular imports
        from models import load_user, Admin, Project, Skill, Certificate
        from routes import init_routes
        
        login_manager.user_loader(load_user)
        init_routes(app)
        
        # Create tables if not exists
        db.create_all()

    # Add security headers
    @app.after_request
    def add_header(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response

    # Add error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('errors/500.html'), 500

    # Add static routes
    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 