from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db = SQLAlchemy(app)

# Define a simple route
@app.route('/')
def home():
    return "Welcome to the Hospital Management System"

# Before first request, create the tables
@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()  # Creates the database tables if they don't exist

if __name__ == '__main__':
    app.run(debug=True)
