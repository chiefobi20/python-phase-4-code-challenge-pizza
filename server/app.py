#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_restaurants():
    all_restaurants = Restaurant.query.all()
    restaurant_dictionary = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in all_restaurants]
    return make_response(jsonify(restaurant_dictionary), 200)

@app.route('/restaurants/<int:id>')
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)

    if restaurant:
        return make_response(jsonify(restaurant.to_dict(rules=('-restaurant_pizzas.pizza', '-restaurant_pizzas.restaurant'))), 200)
    else:
        response_body = {
            "error": "Restaurant not found"
        }
        return make_response(jsonify(response_body), 404)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)

    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)
    else:
        response_body = {
            "error": "Restaurant not found"
        }
        return make_response(jsonify(response_body), 404)

@app.route('/pizzas')
def get_pizzas():
    all_pizzas = Pizza.query.all()
    all_pizzas_dictionaries_list = [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in all_pizzas]
    return make_response(jsonify(all_pizzas_dictionaries_list), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def add_restaurant_pizza():
    price = request.json.get('price')
    pizza_id = request.json.get('pizza_id')
    restaurant_id = request.json.get('restaurant_id')
    try:
        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        response_body = new_restaurant_pizza.to_dict()
        return make_response(jsonify(response_body), 201)
    except:
        response_body = {
            "errors": ["validation errors"]
        }
        return make_response(response_body, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
