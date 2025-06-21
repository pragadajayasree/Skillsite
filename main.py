import smtplib

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from form import LoginForm, RegisterForm, ContactForm, AddSkillForm, Update
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(Users, user_id)


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    skills = relationship("Skills", back_populates='user')


class Skills(UserMixin, db.Model):
    __tablename__ = "skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    skill_name: Mapped[str] = mapped_column(String, nullable=False)
    skill_level: Mapped[str] = mapped_column(String, nullable=False)
    skill_source: Mapped[str] = mapped_column(String, nullable=False)
    projects: Mapped[str] = mapped_column(String)
    user = relationship("Users", back_populates='skills')


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = generate_password_hash(method='pbkdf2:sha256', salt_length=8, password=form.password.data)
            username = form.username.data
            user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
            if user:
                flash("already the user exists")
                return redirect(url_for('login'))
            else:
                new_user = Users(
                    email=email,
                    password=password,
                    username=username
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('home'))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = db.session.execute(db.select(Users).where(Users.email == email)).scalar()
            if not user:
                flash("user doesn't exists,please register")
                return redirect(url_for('register'))
            elif not check_password_hash(user.password, password):
                flash("entered wrong password,please check the password once")
                return redirect(url_for('login'))
            else:
                login_user(user)
                return redirect(url_for('home'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        username = form.username.data
        email = form.email.data
        message = form.message.data
        from_email = os.environ['FROM_EMAIL']
        to_email = os.environ['TO_EMAIL']
        password = os.environ['PASSWORD']
        with smtplib.SMTP(host='smtp.gmail.com', port=587) as connection:
            connection.starttls()
            connection.login(user=from_email, password=password)
            connection.sendmail(from_addr=from_email, to_addrs=to_email, msg=f"subject:Message by user\n\n"
                                                                             f"username:{username}\n"
                                                                             f"email:{email}\n"
                                                                             f"message:{message}")

        return redirect(url_for('home'))

    return render_template("contact.html", form=form)


@app.route('/skills')
@login_required
def skills():
    user_id = current_user.id
    user_skills = db.session.execute(db.select(Skills).where(Skills.user_id == user_id)).scalars().all()
    return render_template("skills.html", skills=user_skills, current_user=current_user)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddSkillForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            level = form.level.data
            source = form.source.data
            projects = form.projects.data
            new_skill = Skills(
                user_id=current_user.id,
                skill_name=name,
                skill_level=level,
                skill_source=source,
                projects=projects
            )
            db.session.add(new_skill)
            db.session.commit()
            return redirect(url_for('skills'))

    return render_template("add.html", form=form, current_user=current_user)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = Update()
    record = db.session.execute(db.select(Skills).where(Skills.id == id, Skills.user_id == current_user.id)).scalar()
    if request.method == 'POST':
        if form.validate_on_submit():
            record.skill_level = form.new_level.data
            record.projects =form.new_projects.data
            db.session.commit()
            return redirect(url_for('skills'))
    form.new_level.data = record.skill_level
    form.new_projects.data = record.projects
    return render_template('update.html', id=id, form=form, current_user=current_user)


@app.route('/delete')
@login_required
def delete():
    id = request.args.get('id')
    record = db.session.execute(db.select(Skills).where(Skills.id == id, Skills.user_id == current_user.id))
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('skills'))


if __name__ == "__main__":
    app.run(debug=True)
