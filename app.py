from flask import Flask, render_template, request, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///exercise_db'
app.config['SECRET_KEY'] = 'tastycakes123'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def root():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        flash('Successfully Registered.', 'success')
        return redirect(f'/users/{user.username}')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome, {user.username}', 'success')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid Username/Password']
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user(username):
    if 'username' not in session or username != session['username']:
        flash('Please Log In.', 'danger')
        return redirect('/login')        
    user = User.query.get(f'{username}')
    return render_template('user.html', user=user)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in session or username != session['username']:
        flash('Please Log In.', 'danger')
        return redirect('/login')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_post = Feedback(title=title, content=content, username=username)
        db.session.add(new_post)
        db.session.commit()
        flash('Comment Added.', 'success')
        return redirect(f'/users/{new_post.username}')
    return render_template('/new.html', form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=['GET', 'POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if 'username' not in session or feedback.username != session['username']:
        flash('Please Log In.', 'danger')
        return redirect('/login')    
    else:
    # form = DeleteForm()
    # if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.username}')