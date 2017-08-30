from app import app, db
from model import Blog, User
from flask import flash, render_template, redirect, request, session
from helpers import validate_signup, validate_login, validate_post, check_hash


@app.before_request
def require_login():
    blocked_routes = ['new_post', 'delete_post']
    if request.endpoint in blocked_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    title_header='Bloggers'
    users = User.query.all()
    return render_template('index.html', 
        base_title=title_header,
        base_header=title_header,
        users=users)

@app.route('/blog', methods=['GET'])
@app.route('/blog/<int:page>', methods=['GET'])
def blog(page=1):
    title_header = 'Blog Posts'
    per_page = 5
    post = Blog.query.filter_by(id=request.args.get('id')).first()

    if post:
        return render_template('post.html',
            base_title=title_header,
            base_header=post.title,
            post=post)
    else:
        all_blogs = Blog.query.order_by(Blog.id.desc()).paginate(page,per_page,error_out=False)
        return render_template('blog.html',
            base_title=title_header,
            base_header=title_header,
            blogs=all_blogs)

@app.route('/blog/<username>', methods=['GET'])
@app.route('/blog/<username>/<int:page>', methods=['GET'])
def user_blog(username,page=1):
    user = User.query.filter_by(name=username).first()
    per_page = 5

    if not user:
        flash("That user {0}, doesn't exist".format(username), 'error')
        return redirect('/')
    else:
        title_header = "{0}'s Blog Posts".format(user.name.title())
        user_blogs = Blog.query.filter_by(owner_id=user.id).order_by(Blog.id.desc()).paginate(page,per_page,error_out=False)
        return render_template('user_blog.html',
            base_title=title_header,
            base_header=title_header,
            user=user,
            blogs=user_blogs)


@app.route('/newpost', methods=['GET','POST'])
def new_post():
    title_header = 'Add Blog Post'
    user = User.query.filter_by(name=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        validation = validate_post(title, body)

        if validation == True:
            new_blog = Blog(title, body, user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        else:
            return render_template('new_post.html',
                base_title=title_header,
                base_header=title_header,
                title=title,
                title_err=validation['title_err'],
                body=body,
                body_err=validation['body_err'])
    else:
        return render_template('new_post.html',
            base_title=title_header, 
            base_header=title_header)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title_header = 'Signup'
    if request.method== 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(name=username).first()
        validation = validate_signup(username, email, password, verify)

        if validation == True and not existing_user:
            new_user = User(username, email, password)
            db.session.add(new_user)
            db.session.commit()

            session['username'] = new_user.name
            flash("Registered as " + new_user.name, 'info')
            return redirect('/newpost')
        else:
            flash("Signup Failed!", 'error')
            return render_template('signup.html',
                base_title=title_header,
                base_header=title_header,
                username=username,
                username_err=validation['username_err'],
                email=email,
                email_err=validation['email_err'],
                password_err=validation['password_err'],
                verify_err=validation['verify_err'])
    else:
        return render_template('signup.html', base_title=title_header, base_header=title_header)

@app.route('/login', methods=['GET', 'POST'])
def login():
    title_header = 'Login'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(name=username).first()
        validation = validate_login(user, password)

        if validation == True:
            session['username'] = user.name
            flash("Welcome " + session['username'], 'info')
            return redirect('/newpost')
        else:
            flash("Login Failed!", 'error')
            return render_template('login.html',
                base_title=title_header,
                base_header=title_header,
                username=username,
                username_err=validation['username_err'],
                password_err=validation['password_err'])
    else:
        return render_template('login.html', 
            base_title=title_header,
            base_header=title_header)

@app.route('/logout')
def logout():
    if 'username' not in session:
        flash("Not logged into any User", 'error')
        return redirect('/blog')
    else:
        flash("Goodbye " + session['username'].title(), 'info')
        del session['username']
        return redirect('/blog')

if __name__ == "__main__":
    app.run()

# TODO - 'Delete' Post functionality
# @app.route('/delpost', methods=['POST'])
# def delete_post():

#     blog_id = int(request.form['blog-id'])
#     post = Blog.query.get(blog_id)
#     db.session.remove(post)
#     db.session.commit()

#     return redirect('/blog')