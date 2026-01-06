import os
import pandas as pd
from app.models import db
from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from app.models.all_models import Role, User,DebtCase,AIModelPrediction,AuditLog,CaseActivityLog,CaseAssignment,CaseClosure,CaseEscalation,DCAPerformanceMetric,Organization,SLADefinition,CaseSLATracking # Import everything needed for setup
from flask_security import Security, SQLAlchemyUserDatastore, login_required, roles_accepted, user_registered, current_user
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Extensions globally
migrate = Migrate()
user_datastore = None # Will be defined inside create_app

# 1. Define the Signal Handler OUTSIDE create_app
def assign_default_role(sender, user, **extra):
    """Automatically assigns 'agent' role to new registrants."""
    agent_role = Role.query.filter_by(name='agent').first()
    if agent_role:
        # We use the app's current security datastore
        from flask import current_app
        current_app.security.datastore.add_role_to_user(user, agent_role)
        db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 2. Link Extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 3. Setup Flask-Security-Too
    global user_datastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    # 4. Connect the Signal
    user_registered.connect_via(app)(assign_default_role)

    # 5. Database & Role Initialization
    with app.app_context():
        db.create_all() 

        # Unified Role Creation (Covers Admin, Manager, and Agent)
        roles = {
            'admin': 'FedEx Corporate Admin',
            'manager': 'DCA Agency Manager',
            'agent': 'Field Collection Agent'
        }
        
        for name, desc in roles.items():
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=desc))
        
        db.session.commit()

    # --- ROUTES ---

    @app.route('/')
    def home():
        return render_template("index.html")
    
    @app.route("/dashboard")
    @login_required
    def dashboard():
        cases = DebtCase.query.all()
        return render_template("dashboard.html", cases=cases)
    
    @app.route('/upload', methods=['POST'])
    @login_required
    @roles_accepted("admin") # Only Admin can upload
    def upload_file():
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '' or not file:
            return redirect(request.url)

        df = pd.read_excel(file)
        for _, row in df.iterrows():
            case = DebtCase(
                tracking_number=str(row['Tracking Number']),
                customer_name=row['Customer Name'],
                amount_due=float(row['Amount']),
            )
            db.session.add(case)
        
        db.session.commit()
        flash('Excel Data Uploaded Successfully!')
        return redirect(url_for('dashboard'))

    @app.route('/update-status/<int:id>', methods=['POST'])
    @login_required
    def update_status(id):
        case = DebtCase.query.get_or_404(id)
        case.status = request.form.get('status')
        db.session.commit()
        flash(f"Case {case.tracking_number} updated to {case.status}")
        return redirect(url_for('dashboard'))

    @app.route('/delete-case/<int:id>', methods=['POST'])
    @login_required
    @roles_accepted("admin") # Only Admin should delete
    def delete_case(id):
        case = DebtCase.query.get_or_404(id)
        db.session.delete(case)
        db.session.commit()
        flash("Record deleted successfully")
        return redirect(url_for('dashboard'))


        # This makes 'has_role' work inside your HTML templates
    @app.context_processor
    def utility_processor():
        return dict(has_role=lambda role: current_user.has_role(role))



    # --- ERROR HANDLERS ---

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def access_denied(e):
        return render_template('errors/403.html'), 403





    return app