from flask import make_response, render_template, request, redirect
from flask_login import login_user
from flask_restful import Resource

from src.models import User


class Login(Resource):
    def get(self):
        return make_response(render_template('login.html'), 200)

    def post(self):
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect('/home')
        else:
            return 'Invalid username/password combination', 400
