from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, Email


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email(), Length(min=6, max=120)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20)])


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email(), Length(min=6, max=120)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20)])
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=20)])


class ContactForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[InputRequired(), Email(), Length(min=6, max=120)])
    message = TextAreaField("Your message", validators=[InputRequired(), Length(min=5, max=1000)])


class AddSkillForm(FlaskForm):
    name = StringField("Course Name", validators=[InputRequired()])
    level = SelectField("Course Level",
                        choices=[('', 'Select Level'), ('Excellent', 'Excellent'), ('Average', 'Average'),
                                 ('Bad', 'Bad')], validators=[InputRequired()]
                        )
    source = StringField("Source", validators=[InputRequired()])
    projects = TextAreaField("Your Projects")


class Update(FlaskForm):
    new_level = SelectField("Course Level",
                            choices=[('', 'Select Level'), ('Excellent', 'Excellent'), ('Average', 'Average'),
                                     ('Bad', 'Bad')], validators=[InputRequired()]
                            )
    new_projects = TextAreaField("Your Projects")
