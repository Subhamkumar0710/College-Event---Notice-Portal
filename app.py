from functools import wraps
from flask import Flask, jsonify, render_template, redirect, flash, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///groceri.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'subhamkumar'

db = SQLAlchemy(app)

class User(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    enrollment= db.Column(db.String(32) ,unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=True)
    password= db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, nullable = False, default = False)

    def check_password(self, password):
        return check_password_hash(self.password,password)

    def to_json(self):
        return{
            'id': self.id,
            'enrollment': self.enrollment,
            'name': self.name,
            'is_admin': self.is_admin
        }

class Events(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(512))
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    description =  db.Column(db.String(512))
    location = db.Column(db.String(64), nullable=False)
    department = db.Column(db.String(64))
    create_at = db.Column(db.DateTime)

    def to_json(self):
        return {
            'id' : self.id,
            'title': self.title,
            'start_date': self.start_date,
            'description':self.description,
            'location': self.location,
            'department': self.department,
            'create_at': self.create_at
        }

class Notice(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String(512))
    content= db.Column(db.String(512))
    department = db.Column(db.String(64))
    posted_at = db.Column(db.DateTime, default=datetime.datetime.now)
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'department': self.department,
            'posted_at': self.posted_at
        }

with app.app_context():
        db.create_all()

with app.app_context():
    admin = User.query.filter_by(enrollment='admin').first()
    if not admin:
        admin = User(enrollment='admin', password=generate_password_hash('admin'), name='admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()



def auth_required(func):
    @wraps(func)
    def inner (*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to login first.')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner


@app.route('/')
@auth_required
def index(): 
    user= User.query.get(session.get('user_id'))
    if user.is_admin:
        return redirect(url_for('admin'))
    query = request.args.get('query', '')
    parameter = request.args.get('parameter', 'title')
    
    if query:
        if parameter == 'title':
            events = Events.query.filter(Events.title.contains(query)).all()
            notices = Notice.query.filter(Notice.title.contains(query)).all()
        # elif parameter == 'department':
            events_ = Events.query.filter(Events.department.contains(query)).all()
            notices_ = Notice.query.filter(Notice.department.contains(query)).all()
            events = events + events_
            notices = notices + notices_
        elif parameter == 'date':
            try:
                date = datetime.datetime.strptime(query, '%Y-%m-%d')
                events = Events.query.filter(Events.start_date == date).all()
                notices = Notice.query.filter(Notice.posted_at == date).all()
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD.')
                return redirect(url_for('index'))
        else:
            flash('Invalid search parameter.')
            return redirect(url_for('index'))
        
        if not events and not notices:
            flash('No results found for your query.')
            events = []
            notices = []
    else:
        events = Events.query.all()
        notices = Notice.query.all()

    event_data = [event.to_json() for event in events]
    notice_data = [notice.to_json() for notice in notices]

    return render_template('index.html', user=user, events=event_data, notices=notice_data, query=query, parameter=parameter)
   
    
    
    
    


@app.route('/admin')
def admin():
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('You are not authorized to view this page.')
        return redirect(url_for('index'))
    
        events = Events.query.all()

    event_data = []
    events = Events.query.all()
    for event in events:
        event_data.append(event.to_json())

    notice_data = []
    notices = Notice.query.all()
    for notice in notices:
        notice_data.append(notice.to_json())
    return render_template('admin.html',user=user,notices=notice_data, events=event_data)
 



@app.route('/login')
def login(): 
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post(): 
    enrollment= request.form.get('enrollment')
    password= request.form.get('password')
    if enrollment == ''or password =='':
        flash('Enrollment or password cannot be empty.')
        return redirect(url_for('login'))
    user = User.query.filter_by(enrollment=enrollment).first()

    if not user:
        flash('User does not exist.')
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash('Incorrect password.')
        return redirect(url_for('login'))
    session['user_id'] = user.id
    if user.is_admin:
        return redirect(url_for('admin'))
    return redirect(url_for('index'))



@app.route('/register')
def register(): 
    return render_template('register.html')

@app.route('/register',methods=['POST'])   
def register_post():
    enrollment = request.form.get('enrollment')
    password = request.form.get('password')
    name = request.form.get('name')
    if enrollment == ''or password =='':
        flash('Enrollment or Password cannot be empty.')
        return redirect(url_for('register'))
    if User.query.filter_by(enrollment=enrollment).first():
        flash('User with this username already exists. Please choose some other username')
        return redirect(url_for('register'))
    user = User(enrollment=enrollment, password=generate_password_hash(password), name=name)
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/profile')
@auth_required
def profile():
    return render_template('profile.html', user=User.query.get(session['user_id']))


@app.route('/profile', methods=['POST'])
@auth_required
def profile_post():
    user = User.query.get(session['user_id'])
    enrollment = request.form.get('enrollment')
    name = request.form.get('name')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    if enrollment == '' or password == '' or cpassword == '':
        flash('Enrollment or password cannot be empty.')
        return redirect(url_for('profile'))
    if not user.cheak_password(cpassword):
        flash('Incorrect password.')
        return redirect(url_for('profile'))
    if User.query.filter_by(enrollment=enrollment).first() and enrollment != user.enrollment:
        flash('User with this username already exists. Please choose some other username')
        return redirect(url_for('profile'))
    user.enrollment = enrollment
    user.name = name
    user.password = password
    db.session.commit()
    flash('Profile updated successfully ')
    return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



@app.route("/event")
def event():
    user = User.query.get(session.get('user_id'))
    events = Events.query.all()
    event_data = [event.to_json() for event in events]
    return render_template('event.html', user=user, events=event_data)
    

@app.route("/event/add")
def add_event():
    return render_template('event/add.html')

@app.route('/event/add', methods=['POST'])
def add_event_post():
    title= request.form.get('title')
    description = request.form.get('description')
    department = request.form.get('department')
    start_date= request.form.get('start_date')
    location = request.form.get('location')
    if title =='':
        flash('Title name cannot be empty.')
        return redirect(url_for('add_event'))
    if description == '':
        flash('Description cannot be empty')
        return redirect(url_for('add_event'))
    if department == '':
        flash('Department cannot be empty.')
        return redirect(url_for('add_event'))
    if start_date == '':
        flash('Start date cannot be empty.')
        return redirect(url_for('add_event'))
    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date.')
        return redirect(url_for('add_event'))
    if location=='':
        flash('Venue cannot be empty.')
        return redirect(url_for('add_event'))
    
    event = Events(title=title, description=description, department=department, start_date=start_date, location= location)
    db.session.add(event)
    db.session.commit()
    flash('Product added successfully.')
    return redirect(url_for('admin', id=event.id))




@app.route("/event/edit/<int:id>")
def edit_event(id):
    event = Events.query.get(id)
    return render_template('event/event.html', event=event)


@app.route("/event/edit/<int:id>",methods=['POST'])
def edit_event_post(id):
    title = request.form.get('title')
    description = request.form.get('description')
    department = request.form.get('department')
    start_date = request.form.get('start_date')
    location = request.form.get('location')
    
    if title == '':
        flash('Title name cannot be empty.')
        return redirect(url_for('edit_event'))
    if description == '':
        flash('Description cannot be empty')
        return redirect(url_for('edit_event'))
    if department == '':
        flash('Department cannot be empty.')
        return redirect(url_for('edit_event'))
    if start_date == '':
        flash('Start date cannot be empty.')
        return redirect(url_for('edit_event'))
    try:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date.')
        return redirect(url_for('edit_event'))
    if location == '':
        flash('Venue cannot be empty.')
        return redirect(url_for('edit_event'))
    event = Events.query.get(id)
    event.title = title
    event.description = description
    event.department = department
    event.start_date = start_date
    event.location = location
    db.session.commit()
    flash('Event updated successfully.')
    return redirect(url_for('admin', id=event.id))
    



@app.route("/event/delete/<int:id>")
def delete_event(id):
    event = Events.query.get(id)
    if not event:
        flash('Event not found.')
        return redirect('/admin')
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully.')
    return redirect(url_for('admin'))
    



@app.route('/notice')
def notice():
    user= User.query.get(session.get('user_id'))
    notices = Notice.query.all()
    notice_data = [notice.to_json() for notice in notices]
    return render_template('notice.html', user=user, notices=notice_data)



@app.route("/notice/add")
def add_notice():
    return render_template('notice/add.html')


@app.route('/notice/add', methods=['POST'])
def add_notice_post():
    title= request.form.get('title')
    content= request.form.get('content')
    department = request.form.get('department')
    posted_at = request.form.get('posted_at')
    if title =='':
        flash('Title name cannot be empty.')
        return redirect(url_for('add_notice'))
    if content == '':
        flash('Content cannot be empty')
        return redirect(url_for('add_notice'))
    if department == '':
        flash('Department cannot be empty.')
        return redirect(url_for('add_notice'))
    if posted_at == '':
        flash('Posted date cannot be empty.')
        return redirect(url_for('add_notice'))
    try:
        posted_at = datetime.datetime.strptime(posted_at, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date.')
        return redirect(url_for('add_notice'))
    
    notice = Notice(title=title, content=content, department=department, posted_at=posted_at)
    db.session.add(notice)
    db.session.commit()
    flash('Notice added successfully.')
    return redirect(url_for('admin', id=notice.id))
    

@app.route("/notice/edit/<int:id>")
def edit_notice(id):
    notice = Notice.query.get(id)
    return render_template('notice/edit.html' , notice=notice)

@app.route("/notice/edit/<int:id>", methods=['POST'])
def edit_notice_post(id):
    title = request.form.get('title')
    content = request.form.get('content')
    department = request.form.get('department')
    posted_at = request.form.get('posted_at')
    if title == '':
        flash('Title name cannot be empty.')
        return redirect(url_for('edit_notice'))
    if content == '':
        flash('Content cannot be empty')
        return redirect(url_for('edit_notice'))
    if department == '':
        flash('Department cannot be empty.')
        return redirect(url_for('edit_notice'))
    if posted_at == '':
        flash('Posted date cannot be empty.')
        return redirect(url_for('edit_notice'))
    try:
        posted_at = datetime.datetime.strptime(posted_at, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date.')
        return redirect(url_for('edit_notice'))
    notice = Notice.query.get(id)
    notice.title = title
    notice.content = content
    notice.department = department
    notice.posted_at = posted_at
    db.session.commit()
    flash('Notice updated successfully.')
    return redirect(url_for('admin', id=notice.id))   


@app.route("/notice/delete/<int:id>")
def delete_notice(id):
    notice = Notice.query.get(id)
    if not notice:
        flash('Notice not found.')
        return redirect('/admin')
    db.session.delete(notice)
    db.session.commit()
    flash('Notice deleted successfully.')
    return redirect(url_for('admin'))






if __name__ == "__main__":
     
    app.run(debug=True)


