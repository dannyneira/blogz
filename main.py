from flask import Flask, request, redirect, session, render_template, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
from random import choice
import string

app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:root@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f72746fd810a750dbee37dc116c2aa6aaf070df82d0bd7edb42bfbb42c96e9b3'

def gen_hash(password, seed=None):
    if not seed:
        seed = "".join(choice(string.ascii_letters) for i in range(5))
    return "{0},{1}".format(sha256(str.encode(password+seed)).hexdigest(),seed)

def check_hash(hash, password):
    hash,seed = hash.split(',')
    return True if hash[0] == sha256(str.encode(password+hash[1])).hexdigest() else False

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(480))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET'])
def blog():
    title_header = 'Build-A-Blog'
    post = Blog.query.filter_by(id=request.args.get('id')).first()
    if post:
        return render_template('post.html',
            base_title=title_header,
            header=post.title,
            body=post.body)

    blogs = sorted(Blog.query.all(), key=lambda x: x.id, reverse=True)
    return render_template('blog.html',
        base_title=title_header,
        header=title_header,
        blogs=blogs)

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    title_header = 'Add Blog Post'
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        errors = {'title_err':"", 'body_err':""}

        if title == '':
            errors['title_err'] = 'Please fill in Title'
        if body == '':            
            errors['body_err'] = 'Please fill in Body'

        if any("" != err for err in errors.values()):
            return render_template('newpost.html',
                base_title=title_header,
                header=title_header,
                title=title,
                body=body,
                title_err=errors['title_err'],
                body_err=errors['body_err'])
        else:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
    else:
        return render_template('newpost.html', base_title=title_header, header=title_header)

if __name__ == "__main__":
    app.run()

# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'register']
#     if request.endpoint not in allowed_routes and 'email' not in session:
#         return redirect('/login')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method== 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         verify = request.form['verify']

#         # validate user data
#         existing_user = User.query.filter_by(email=email).first()
#         validation = validate_signup(email,password,verify)

#         if validation == True and not existing_user:
#             new_user = User(email, make_pw_hash(password))
#             db.session.add(new_user)
#             db.session.commit()

#             session['email'] = email
#             flash("Registered as " + email, 'info')
#             return redirect('/')
#         else:
#             flash("Registration Failed!", 'error')
#             return render_template('register.html',
#                 title='Register',
#                 email=validation['email'],
#                 email_err=validation['email_err'],
#                 password_err=validation['password_err'],
#                 verify_err=validation['verify_err'])
#     else:        
#         return render_template('register.html', title='Register')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = User.query.filter_by(email=email).first()
#         validation = validate_login(user, password)

#         if validation == True:
#             session['email'] = email
#             flash("Welcome "+email, 'info')
#             return redirect('/')
#         else:
#             flash("Login Failed!", 'error')
#             return render_template('login.html',
#                 title='Login Error!',
#                 email=validation['email'],
#                 email_err=validation['email_err'],
#                 password_err=validation['password_err'])
#     else:
#         return render_template('login.html', title='Login')

# @app.route('/logout')
# def logout():
#     flash("Goodbye "+session['email'], 'info')
#     del session['email']
#     return redirect('/')

# @app.route('/delete-task', methods=['POST'])
# def delete_task():

#     task_id = int(request.form['task-id'])
#     task = Task.query.get(task_id)
#     task.completed = True

#     db.session.add(task)
#     db.session.commit()

#     return redirect('/')