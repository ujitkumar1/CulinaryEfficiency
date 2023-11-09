from flask import make_response, render_template
from flask_login import login_required
from flask_restful import Resource

from src.helperFunctions import Help


class Order(Resource):
    @login_required
    def get(self):
        food = Help.fetchMenu()
        return make_response(render_template('order-page.html', menu=food), 200)
