from random import choice, randint
from flask_migrate import Migrate
from wtforms.validators import DataRequired, NumberRange, Optional, Email
from wtforms import FloatField, IntegerField, SubmitField, ValidationError
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

from config import Config
from news import parse_news

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "auth"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    financial_data = db.relationship('FinancialData', backref='user', uselist=False)


class FinancialData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    profit = db.Column(db.Float, nullable=True)
    expenses = db.Column(db.Float, nullable=True)
    investments = db.Column(db.Float, nullable=True)
    new_clients = db.Column(db.Integer, nullable=True)
    avg_income_per_client = db.Column(db.Float, nullable=True)
    avg_client_lifetime = db.Column(db.Float, nullable=True)
    orders = db.Column(db.Integer, nullable=True)
    initial_investments = db.Column(db.Float, nullable=True)
    annual_net_income = db.Column(db.Float, nullable=True)


with app.app_context():
    db.create_all()


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(
        min=4, max=150)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[InputRequired(), Length(
        min=4, max=150)], render_kw={"placeholder": "Password"})


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(
        min=4, max=150)], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[InputRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(
        min=4, max=150)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use.')


class FinancialDataForm(FlaskForm):
    profit = FloatField('Прибыль', validators=[Optional(), NumberRange(min=0)])
    expenses = FloatField('Расходы', validators=[Optional(), NumberRange(min=0)])
    investments = FloatField('Инвестиции', validators=[Optional(), NumberRange(min=0)])
    new_clients = IntegerField('Количество новых клиентов', validators=[Optional(), NumberRange(min=0)])
    avg_income_per_client = FloatField('Средний доход с клиента', validators=[Optional(), NumberRange(min=0)])
    avg_client_lifetime = FloatField('Среднее время взаимоотношений с клиентом',
                                     validators=[Optional(), NumberRange(min=0)])
    orders = IntegerField('Количество заказов', validators=[Optional(), NumberRange(min=0)])
    initial_investments = FloatField('Начальные инвестиции', validators=[Optional(), NumberRange(min=0)])
    annual_net_income = FloatField('Ежегодный чистый доход', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Save Changes')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/home')
@login_required
def home():
    finance_data: FinancialData = current_user.financial_data
    data = {
        "CAC": 0,
        "CLV": 0,
        "ROI": 0,
        "AOV": 0,
        "payback_period": 0,
        "CPA": 0
    }
    if finance_data.expenses:
        data = {
            "CAC": finance_data.expenses // finance_data.new_clients,
            "CLV": finance_data.avg_income_per_client * finance_data.avg_client_lifetime,
            "ROI": (finance_data.profit - finance_data.investments) // finance_data.investments * 100,
            "AOV": finance_data.profit // finance_data.orders,
            "payback_period": finance_data.initial_investments // finance_data.annual_net_income,
            "CPA": finance_data.expenses // finance_data.new_clients
        }
    news = choice(parse_news())
    return render_template('home.html', current_user=current_user, **data, news=news)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    financial_data = current_user.financial_data
    if not financial_data:
        financial_data = FinancialData(user_id=current_user.id)
        db.session.add(financial_data)
        db.session.commit()

    form = FinancialDataForm(obj=financial_data)
    if form.validate_on_submit():
        form.populate_obj(financial_data)
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('profile.html', form=form, current_user=current_user)


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    login_form = LoginForm()
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        username = register_form.username.data
        email = register_form.email.data
        password = register_form.password.data
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth'))

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 401

    return render_template('auth.html', register_form=register_form, login_form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth'))


if __name__ == "__main__":
    app.run(debug=True)
