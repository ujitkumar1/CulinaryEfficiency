from flask import make_response, render_template, request
from flask_login import login_required
from flask_restful import Resource

from src import db
from src.helperFunctions import Help
from src.models import Orders


class placeOrder(Resource):
    @login_required
    def post(self):
        last_id = Orders.query.order_by(Orders.id.desc()).first().id
        new_id = last_id + 1 if last_id is not None else 1
        orders = Help.fetchOrderData(request.form)
        for oneOrder in orders:
            placeorder = Orders(id=new_id, item=oneOrder[1], qty=oneOrder[3], price=(oneOrder[3] * oneOrder[2]))
            db.session.add(placeorder)
            db.session.commit()
        return make_response(render_template('after-order.html', orderItems=orders), 200)
