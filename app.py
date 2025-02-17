from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Define Models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'doctor', 'patient', etc.

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(15))

    user = db.relationship('User', backref=db.backref('patient', uselist=False))

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(15))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_time = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Pending')

    patient = db.relationship('Patient', backref=db.backref('appointments'))
    doctor = db.relationship('Doctor')

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_issued = db.Column(db.String(100), nullable=False)
    payment_status = db.Column(db.String(50), default='Unpaid')

    patient = db.relationship('Patient', backref=db.backref('bills'))

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

# User Login/Logout/Registration

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Hash password before storing
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))

        flash('Invalid credentials', 'danger')

    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Dashboard

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('dashboard.html', role='admin')
    elif current_user.role == 'doctor':
        return render_template('dashboard.html', role='doctor')
    elif current_user.role == 'patient':
        return render_template('dashboard.html', role='patient')

# Patient's Appointments (Patient-Specific Functionality)

@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    if current_user.role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if request.method == 'POST':
            doctor_id = request.form['doctor_id']
            appointment_time = request.form['appointment_time']
            new_appointment = Appointment(patient_id=patient.id, doctor_id=doctor_id, appointment_time=appointment_time)
            db.session.add(new_appointment)
            db.session.commit()
            flash("Appointment booked successfully!", "success")
            return redirect(url_for('appointments'))

        appointments_list = Appointment.query.filter_by(patient_id=patient.id).all()
        doctors = Doctor.query.all()
        return render_template('appointments.html', appointments=appointments_list, doctors=doctors)

    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('dashboard'))

# Doctor's Appointments

@app.route('/doctor/appointments', methods=['GET'])
@login_required
def doctor_appointments():
    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(name=current_user.username).first()
        appointments_list = Appointment.query.filter_by(doctor_id=doctor.id).all()
        return render_template('doctor_appointments.html', appointments=appointments_list)
    
    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('dashboard'))

# Logout

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
