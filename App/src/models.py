from datetime import datetime

from flask_login import UserMixin

from src import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    price = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(70), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), default=datetime.now().strftime("%B %d, %Y"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
