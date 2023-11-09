from flask import redirect
from flask_login import logout_user, login_required
from flask_restful import Resource


class Logout(Resource):
    @login_required
    def get(self):
        logout_user()
        return redirect('/login')
