from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
from models import Admin, Project, Skill, Certificate
from app import db
from datetime import datetime
from random import randint

def init_routes(app):
    @app.template_filter('datetimeformat')
    def datetimeformat_filter(value, format='%b %d, %Y %I:%M %p'):
        if not value:
            return ''
        return value.strftime(format)

    @app.route('/')
    def home():
        admin = Admin.query.first()
        return render_template('user/home.html', admin=admin)

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            admin = Admin.query.filter_by(username=username).first()
            
            if admin and check_password_hash(admin.password, password):
                login_user(admin)
                return redirect(url_for('admin_dashboard'))
            flash('Invalid credentials')
        return render_template('admin/login.html')

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        projects_count = Project.query.count()
        certificates_count = Certificate.query.count()
        skills_count = Skill.query.count()
        
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(3).all()
        
        recent_activities = [
            {
                'icon': 'chart-line',
                'title': 'Performance Metrics',
                'value': '85%',
                'trend': 'up'
            },
            {
                'icon': 'users',
                'title': 'Monthly Visitors',
                'value': '2.4K',
                'trend': 'up'
            }
        ]
        
        # Generate sample chart data
        chart_labels = [datetime.now().strftime('%a') for _ in range(7)]
        chart_data = {
            'visitors': [randint(50, 200) for _ in range(7)],
            'pageviews': [randint(100, 300) for _ in range(7)]
        }
        
        return render_template('admin/dashboard.html',
                             projects_count=projects_count,
                             certificates_count=certificates_count,
                             skills_count=skills_count,
                             recent_activities=recent_activities,
                             recent_projects=recent_projects,
                             chart_labels=chart_labels,
                             chart_data=chart_data)

    @app.route('/admin/project/add', methods=['GET', 'POST'])
    @login_required
    def add_project():
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            image = request.files.get('image')
            
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
            project = Project(title=title, description=description, image=filename)
            db.session.add(project)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/manage_projects.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/about')
    def about():
        admin = Admin.query.first()
        return render_template('user/about.html', admin=admin)

    @app.route('/certificates')
    def certificates():
        certs = Certificate.query.all()
        return render_template('user/certificates.html', certificates=certs)

    @app.route('/contact')
    def contact():
        return render_template('user/contact.html')

    @app.route('/admin/profile', methods=['GET', 'POST'])
    @login_required
    def admin_profile():
        if request.method == 'POST':
            # Update profile picture
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    current_user.profile_pic = filename
            
            # Update bio
            current_user.bio = request.form.get('bio')
            
            # Update resume
            if 'resume' in request.files:
                file = request.files['resume']
                if file.filename != '':
                    # Remove old resume
                    if current_user.resume:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], current_user.resume))
                    # Save new resume
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    current_user.resume = filename
            
            current_user.home_title = request.form.get('home_title')
            current_user.home_subtitle = request.form.get('home_subtitle')
            
            db.session.commit()
            flash('Profile updated successfully!')
        
        return render_template('admin/profile.html')

    @app.route('/admin/skills', methods=['GET', 'POST'])
    @login_required
    def manage_skills():
        if request.method == 'POST':
            skill_name = request.form.get('name')
            proficiency = request.form.get('proficiency')
            category = request.form.get('category')
            
            new_skill = Skill(
                name=skill_name,
                proficiency=proficiency,
                category=category
            )
            db.session.add(new_skill)
            db.session.commit()
            flash('Skill added successfully!')
        
        skills = Skill.query.all()
        return render_template('admin/manage_skills.html', skills=skills)

    @app.route('/admin/skill/delete/<int:id>')
    @login_required
    def delete_skill(id):
        skill = Skill.query.get_or_404(id)
        db.session.delete(skill)
        db.session.commit()
        flash('Skill deleted successfully!')
        return redirect(url_for('manage_skills'))

    @app.route('/admin/project/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_project(id):
        project = Project.query.get_or_404(id)
        if request.method == 'POST':
            project.title = request.form.get('title')
            project.description = request.form.get('description')
            project.skills = request.form.get('skills')
            
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    # Remove old image
                    if project.image:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], project.image))
                    # Save new image
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    project.image = filename
            
            db.session.commit()
            flash('Project updated successfully!')
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/edit_project.html', project=project)

    @app.route('/admin/project/delete/<int:id>')
    @login_required
    def delete_project(id):
        project = Project.query.get_or_404(id)
        if project.image:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], project.image))
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/skill/edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_skill(id):
        skill = Skill.query.get_or_404(id)
        if request.method == 'POST':
            skill.name = request.form.get('name')
            skill.proficiency = request.form.get('proficiency')
            skill.category = request.form.get('category')
            db.session.commit()
            flash('Skill updated successfully!')
            return redirect(url_for('manage_skills'))
        return render_template('admin/edit_skill.html', skill=skill)

    @app.route('/download-resume')
    def download_resume():
        admin = Admin.query.first()
        if admin and admin.resume:
            return send_from_directory(
                app.config['UPLOAD_FOLDER'],
                admin.resume,
                as_attachment=True
            )
        abort(404)

    @app.route('/skills')
    def skills():
        skills = Skill.query.all()
        return render_template('user/skills.html', skills=skills)

    @app.route('/admin/certificates', methods=['GET', 'POST'])
    @login_required
    def manage_certificates():
        if request.method == 'POST':
            # Handle certificate upload
            title = request.form.get('title')
            organization = request.form.get('organization')
            date_issued = request.form.get('date_issued')
            image = request.files['image']
            credential_id = request.form.get('credential_id')
            credential_url = request.form.get('credential_url')

            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_cert = Certificate(
                title=title,
                organization=organization,
                date_issued=datetime.strptime(date_issued, '%Y-%m-%d'),
                image=filename,
                credential_id=credential_id,
                credential_url=credential_url
            )
            db.session.add(new_cert)
            db.session.commit()
            flash('Certificate added successfully!')

        certificates = Certificate.query.all()
        return render_template('admin/manage_certificates.html', certificates=certificates)

    @app.route('/projects')
    def projects():
        projects = Project.query.all()
        return render_template('user/projects.html', projects=projects)

    @app.route('/google-login')
    def google_login():
        if not current_user.is_anonymous:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('google.login')) 