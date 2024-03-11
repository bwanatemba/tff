from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import InputRequired


class SubMemberForm(FlaskForm):
    full_name = StringField('Full Name', validators=[InputRequired()])
    phone_number = StringField('Phone Number', validators=[InputRequired()])
    constituency = StringField('Constituency', validators=[InputRequired()])
    ward = StringField('Ward', validators=[InputRequired()])
    ward_position = SelectField('Ward Position', choices=[
        ('Chairperson', 'Chairperson'),
        ('Deputy Chairperson', 'Deputy Chairperson'),
        ('Secretary', 'Secretary'),
        ('Deputy Secretary', 'Deputy Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Deputy Treasurer', 'Deputy Treasurer'),
        ('Organizing Secretary', 'Organizing Secretary'),
        ('Deputy Organizing Secretary', 'Deputy Organizing Secretary'),
        ('Youth League', 'Youth League'),
        ('Women League', 'Women League'),
        ('PWD', 'PWD')
    ], validators=[InputRequired()])
