from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_DURATION'] = 3600  # One hour

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.static_folder = 'static'


# Define models
class AuthorizedMember(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15), unique=True)
    constituency = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    password = db.Column(db.String(20))
    is_super_admin = db.Column(db.Boolean, default=False)


class SubMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    constituency = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    ward_position = db.Column(db.String(50))
    authorized_member_id = db.Column(db.Integer, db.ForeignKey('authorized_member.id'))


# Define forms
class SubMemberForm(FlaskForm):
    full_name = StringField('Full Name', validators=[InputRequired()])
    phone_number = StringField('Phone Number', validators=[InputRequired()])
    constituency = StringField('Constituency', validators=[InputRequired()])
    ward = StringField('Ward', validators=[InputRequired()])
    ward_position = SelectField('Ward Position', choices=[('Chairperson', 'Chairperson'),
                                                          ('Deputy Chairperson', 'Deputy Chairperson'),
                                                          ('Secretary', 'Secretary'),
                                                          ('Deputy Secretary', 'Deputy Secretary'),
                                                          ('Treasurer', 'Treasurer'),
                                                          ('Deputy Treasurer', 'Deputy Treasurer'),
                                                          ('Organizing Secretary', 'Organizing Secretary'),
                                                          (
                                                              'Deputy Organizing Secretary',
                                                              'Deputy Organizing Secretary'),
                                                          ('Youth League', 'Youth League'),
                                                          ('Women League', 'Women League'),
                                                          ('PWD', 'PWD')],
                                validators=[InputRequired()])


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return AuthorizedMember.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('base.html')


@app.route('/super_admin_login', methods=['GET', 'POST'])
def super_admin_login():
    if request.method == 'POST':
        # Check if the login credentials are correct
        if request.form['username'] == 'superadmin' and request.form['password'] == 'superadminpassword':
            # Redirect to authorized members page
            return redirect(url_for('authorized_member'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('super_admin_login.html')


# Define the login form for authorized members
class AuthorizedMemberLoginForm(FlaskForm):
    phone_number = StringField('Phone Number', validators=[InputRequired()])
    password = StringField('Password', validators=[InputRequired()])


# Define the login route
@app.route('/authorized_member_login', methods=['GET', 'POST'])
def authorized_member_login():
    form = AuthorizedMemberLoginForm()
    if form.validate_on_submit():
        member = AuthorizedMember.query.filter_by(phone_number=form.phone_number.data).first()
        if member and member.password == form.password.data:
            login_user(member)
            # Redirect to the page to add sub-members
            return redirect(url_for('sub_members_form'))
        else:
            flash('Invalid phone number or password', 'error')
    return render_template('authorized_member_login.html', form=form)


@app.route('/authorized_members', methods=['GET', 'POST'])
def authorized_member():
    if request.method == 'POST':
        # Check if the phone number already exists
        existing_member = AuthorizedMember.query.filter_by(phone_number=request.form['phone_number']).first()
        if existing_member:
            flash('Phone number already exists', 'error')
        else:
            # Generate random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            # Create new authorized member
            new_member = AuthorizedMember(full_name=request.form['full_name'],
                                          phone_number=request.form['phone_number'],
                                          constituency=request.form['constituency'],
                                          ward=request.form['ward'],
                                          password=password)
            db.session.add(new_member)
            db.session.commit()
            flash('New authorized member added successfully!', 'success')
            members = AuthorizedMember.query.all()

            return render_template('authorized_members.html', members=members)
    return render_template('authorized_members.html')


@app.route('/sub_members_form', methods=['GET', 'POST'])
def sub_members_form():
    form = SubMemberForm()
    # Form submission logic for sub-members
    if form.validate_on_submit():
        new_sub_member = SubMember(full_name=form.full_name.data,
                                   phone_number=form.phone_number.data,
                                   constituency=form.constituency.data,
                                   ward=form.ward.data,
                                   ward_position=form.ward_position.data,
                                   authorized_member_id=current_user.id)
        db.session.add(new_sub_member)
        db.session.commit()
        flash('Sub-member details submitted successfully!', 'success')
        return redirect(url_for('success'))
    return render_template('sub_members_form.html', form=form)


@app.route('/full_list')
def full_list():
    # Query all authorized members
    authorized_members = AuthorizedMember.query.all()
    # Create a dictionary to hold each authorized member and their sub-members
    members_with_subs = {}
    for member in authorized_members:
        # Query sub-members for each authorized member
        sub_members = SubMember.query.filter_by(authorized_member_id=member.id).all()
        members_with_subs[member] = sub_members
    # Render the full_list template with the members_with_subs data
    return render_template('full_list.html', members_with_subs=members_with_subs)


@app.route('/authorized_members_list')
def authorized_members_list():
    authorized_members = AuthorizedMember.query.all()
    return render_template('authorized_members_list.html', authorized_members=authorized_members)


@app.route('/constituency_list')
def constituency_list():
    # Query all authorized members and group them by constituency
    constituencies = AuthorizedMember.query.with_entities(AuthorizedMember.constituency).distinct()
    members_by_constituency = {}
    for constituency in constituencies:
        members = AuthorizedMember.query.filter_by(constituency=constituency[0]).all()
        members_by_constituency[constituency] = members
    return render_template('constituency_list.html', members_by_constituency=members_by_constituency)


@app.route('/ward_list')
def ward_list():
    # Query all authorized members and group them by ward
    wards = AuthorizedMember.query.with_entities(AuthorizedMember.ward).distinct()
    members_by_ward = {}
    for ward in wards:
        members = AuthorizedMember.query.filter_by(ward=ward[0]).all()
        members_by_ward[ward] = members
    return render_template('ward_list.html', members_by_ward=members_by_ward)


@app.route('/ward_position_list')
def ward_position_list():
    # Query all sub-members and group them by ward_position
    ward_positions = SubMember.query.with_entities(SubMember.ward_position).distinct()
    members_by_ward_position = {}
    for position in ward_positions:
        members = SubMember.query.filter_by(ward_position=position[0]).all()
        members_by_ward_position[position] = members
    return render_template('ward_position_list.html', members_by_ward_position=members_by_ward_position)


# Define the logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/success')
def success():
    return 'Sub-member details submitted successfully!'


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
