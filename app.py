from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db = SQLAlchemy(app)

# Manually create tables before running the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database tables if they don't exist
    app.run(debug=True)
