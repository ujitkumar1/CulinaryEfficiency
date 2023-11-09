from flask import make_response, render_template
from flask_login import login_required
from flask_restful import Resource


class Analysis(Resource):
    @login_required
    def get(self):
        return make_response(render_template('analysis.html'), 200)
