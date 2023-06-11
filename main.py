from src import app, db, api
from src.analysis import Analysis
from src.dailyanalysis import dailyAnalysis
from src.helperFunctions import Help
from src.home import Home
from src.index import Index
from src.login import Login
from src.logout import Logout
from src.order import Order
from src.placeOrder import placeOrder
from src.todayAnalysis import todayAnalysis
from src.weeklyAnalysis import weeklyAnalysis

api.add_resource(Analysis, "/analysis")
api.add_resource(dailyAnalysis, "/daily-analysis")
api.add_resource(Home, "/home")
api.add_resource(Login, "/login")
api.add_resource(Index, "/")
api.add_resource(Order, "/order")
api.add_resource(placeOrder, "/place-order")
api.add_resource(todayAnalysis, "/today-analysis")
api.add_resource(weeklyAnalysis, "/weekly-analysis")
api.add_resource(Logout, "/logout")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    Help.clean()
    app.run(debug=True)
