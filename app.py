from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import row_data
import utils


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(80))
    phone = db.Column(db.String(80))


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(300))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(120))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# наполнение данными
with app.app_context():
    db.create_all()

    for user_data in row_data.users:
        db.session.add(User(**user_data))
        db.session.commit()

    for order_data in row_data.orders:
        order_data['start_date'] = datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
        order_data['end_date'] = datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
        db.session.add(Order(**order_data))
        db.session.commit()

    for offer_data in row_data.offers:
        db.session.add(Offer(**offer_data))
        db.session.commit()


# представления(вьюшки)
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        users = User.query.all()
        response = []
        for user in users:
            response.append(utils.users_to_dict(user))
        return jsonify(response)

    elif request.method == 'POST':
        users_data = request.json
        db.session.add(User(**users_data))
        db.session.commit()
        return 'user_added'


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])
def user(uid: int):
    user_data = User.query.get(uid)

    if request.method == 'GET':
        return jsonify(utils.users_to_dict(user_data))

    elif request.method == 'DELETE':
        db.session.delete(user_data)
        db.session.commit()
        return 'user_deleted'

    elif request.method == 'PUT':
        data = request.json

        user_data.first_name = data['first_name']
        user_data.last_name = data['last_name']
        user_data.role = data['role']
        user_data.phone = data['phone']
        user_data.email = data['email']
        user_data.age = data['age']
        db.session.add(user_data)
        db.session.commit()
        return 'user_changed'


@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = Order.query.all()
        response = []
        for order in orders:
            response.append(utils.orders_to_dict(order))
        return jsonify(response)

    elif request.method == 'POST':
        data = request.json

        order = Order(
            name=data['name'],
            description=data['description'],
            start_date=datetime.strptime(data['start_date'], '%Y/%m/%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y/%m/%d').date(),
            price=data['price'],
            customer_id=data['customer_id'],
            executor_id=data['executor_id']
        )
        db.session.add(order)
        db.session.commit()
        return jsonify(data)


@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def order(oid: int):
    order_data = Order.query.get(oid)

    if request.method == 'GET':
        return jsonify(utils.orders_to_dict(order_data))

    elif request.method == 'DELETE':
        db.session.delete(order_data)
        db.session.commit()
        return 'order_deleted'

    elif request.method == 'PUT':
        data = request.json

        order_data.name = data['name']
        order_data.description = data['description']
        order_data.start_date = datetime.strptime(data['start_date'], '%Y/%m/%d').date()
        order_data.end_date = datetime.strptime(data['end_date'], '%Y/%m/%d').date()
        order_data.price = data['price']
        order_data.customer_id = data['customer_id']
        order_data.executor_id = data['executor_id']
        db.session.add(order_data)
        db.session.commit()
        return 'order_changed'


@app.route('/offers', methods=['GET', 'POST'])
def offers():
    if request.method == 'GET':
        offers = Offer.query.all()
        response = []
        for offer in offers:
            response.append(utils.offers_to_dict(offer))
        return jsonify(response)

    elif request.method == 'POST':
        data = request.json

        offer = Offer(
            order_id=data['order_id'],
            executor_id=data['executor_id']
        )
        db.session.add(offer)
        db.session.commit()
        return 'offer_added'


@app.route('/offers/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def offer(oid: int):
    offer_data = Offer.query.get(oid)

    if request.method == 'GET':
        return jsonify(utils.offers_to_dict(offer_data))

    elif request.method == 'DELETE':
        db.session.delete(offer_data)
        db.session.commit()
        return 'offer_deleted'

    elif request.method == 'PUT':
        data = request.json

        offer.order_id = data['order_id']
        offer.executor_id = data['executor_id']
        db.session.add(offer_data)
        db.session.commit()
        return 'offer_changed'


if __name__ == '__main__':
    app.run()
