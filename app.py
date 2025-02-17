from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()  # Creates the database tables if they don't exist

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
     with app.app_context():
        db.create_all()  
    app.run(debug=True)
