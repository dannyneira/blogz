from flask import Flask, request, redirect, session, render_template, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from helpers import validate_signup, validate_login, gen_hash, check_hash
from datetime import date

app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f72746fd810a750dbee37dc116c2aa6aaf070df82d0bd7edb42bfbb42c96e9b3'