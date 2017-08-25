from flask import Flask, request, redirect, session, render_template, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from helpers import validate_signup, validate_login, gen_hash, check_hash
from datetime import date
from main import app

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(480))
    date = db.Column(db.Date)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.date = date.today()
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
