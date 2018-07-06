from flask import Flask,jsonify
from flask_pymongo import PyMongo, pymongo
from flask_cors import CORS
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'login_test'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
CORS(app)


class ProductSchema(Schema):
    product_id = fields.Str()
    product_name = fields.Str()
    username = fields.Str()
    Product_type = fields.Str()
    product_description = fields.Str()
    price_per_qty = fields.Str()
    product_quantity = fields.Str()
    delivery_day = fields.Str()
    no_orders = fields.Number()
    product_create_dt = fields.Str()


mongo = PyMongo(app)


@app.route('/createproducts', methods=['POST', 'GET'])
def createproducts():

    product_snapshot = mongo.db.supplier
    i = product_snapshot.insert_one({'product_id': 'pname', 'product_name': 'productname', 'username': 'user', 'Product_type': 'Producttype', 'product_description': 'description',
                                     'price_per_qty': 'price_per_qty', 'product_quantity': 'quantity', 'delivery_day': 'delivery_day', 'no_orders': 0, 'product_create_dt': 'pcreate_dt'})
    print(i)
    return "1"


@app.route('/showproducts', methods=['POST', 'GET'])
def showproducts():

    product_snapshot = mongo.db.supplier
    product_snapshot = product_snapshot.find()
    schema = ProductSchema(many=True)
    products = schema.dump(product_snapshot)
    return jsonify(products.data)


@app.route('/')
def hello_world():
    return 'Hello World'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
