from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.Integer, unique=False, nullable=False)
    text = db.Column(db.String(100), unique=False, nullable=False)
    image = db.Column(db.String(30), unique=True, nullable=False)
    solution = db.Column(db.String(100), unique=False, nullable=False)
    image_solution = db.Column(db.String(30), unique=True, nullable=False)
