from flask import Flask, render_template, request, session , url_for , redirect,json
from flask_pymongo import PyMongo,pymongo
from random import randint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
import datetime


app = Flask(__name__)

app.config.update(
    DEBUG = True
)


app.config['MONGO_DBNAME'] = 'login_test'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/'

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "/%s" % (self.uid)
    
    def __eq__(self, other):
            '''
            Checks the equality of two `UserMixin` objects using `get_id`.
            '''
            if isinstance(other, UserMixin):
                return self.get_id() == other.get_id()
            return NotImplemented

mongo = PyMongo(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route('/home')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/ostatus')
@login_required
def ostatus():
    return render_template('OrderStatus.html')
    

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route('/')
def index():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        # if "POST" in rule.methods:
        print(rule.endpoint)
        url = url_for(rule.endpoint, **(rule.defaults or {}))
        links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
        return json.dumps(links)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/create')
@login_required
def create():
    return render_template('B_Success.html')

@app.route('/createproduct' , methods=['GET'])
@login_required
def createproduct():
    return render_template('Add_Product.html')

@app.route('/addproduct', methods=['POST'])
def addproduct():
    if request.method == 'POST':
        supplier = mongo.db.supplier
        user=session['username']
        data=request.json['info']
        productname = data['productname'] 
        pname = productname+'_'+str(randint(10000,99999))
        Producttype = data['Producttype']  
        description=data['description']
        price_per_qty=data['price']
        quantity=data['quantity']
        delivery_day=data['delivery']
        now = datetime.datetime.now()
        pcreate_dt= now.strftime("%Y-%m-%d %H:%M")
        supplier.insert({'_id':pname,'product_id':pname,'product_name' : productname , 'username' : user,'Product_type' : Producttype,'product_description' : description,'price_per_qty' : price_per_qty,'product_quantity': quantity,'delivery_day': delivery_day, 'no_orders': 0 ,'product_create_dt': pcreate_dt})
        
        
    return redirect(url_for('createproduct'))
    
@app.route('/showallproducts',methods=['POST','GET'])
@login_required
def showallproducts():
    return render_template('showallproducts.html')

@app.route('/showproducts',methods=['POST','GET'])
@login_required
def showproducts():

     product_snapshot = mongo.db.supplier
     product_snapshot = product_snapshot.find()

     productSnapShot=[]
     for productStatus in product_snapshot:
        qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        oSnapshot={
                'product_id': productStatus['product_id'],
                'product_name': productStatus['product_name'],
                'product_description': productStatus['product_description'],
                'price_per_qty' : productStatus['price_per_qty'],
                'product_quantity' :qty,
                'delivery_day' : productStatus['delivery_day']
                }
        productSnapShot.append(oSnapshot)

     return json.dumps(productSnapShot)
@app.route('/showoneproduct',methods=['POST','GET'])
@login_required
def showoneproduct():
     product_snapshot = mongo.db.supplier
     pname=request.json['id']
     product_snapshot = product_snapshot.find({'product_id':pname})
     productSnapShot=[]
     for productStatus in product_snapshot:
        oSnapshot={
                'product_id': productStatus['product_id'],
                'product_name': productStatus['product_name'],
                'product_description': productStatus['product_description'],
                'price_per_qty' : productStatus['price_per_qty'],
                                                          'product_quantity' : productStatus['product_quantity'],
                                                          'delivery_day' : productStatus['delivery_day']
                }
        productSnapShot.append(oSnapshot)
     return json.dumps(productSnapShot)
              
@app.route('/updateProduct',methods=['POST'])
def updateProduct():
    if request.method == 'POST':
        supplier = mongo.db.supplier
        user=session['username']
        productinfo=request.json['info']
        pname = productinfo['product_name'] 
        product_id=productinfo['product_id']
        price_per_qty=productinfo['price_per_qty']
        quantity=productinfo['product_quantity']
        delivery_day=productinfo['delivery_day']
        now = datetime.datetime.now()
        pcreate_dt= now.strftime("%Y-%m-%d %H:%M")
        supplier.update_one({'product_id':product_id},{'$set':{'product_name' : pname , 'username' : user,'price_per_qty' : price_per_qty,'product_quantity': quantity,'delivery_day': delivery_day,'product_create_dt': pcreate_dt}})
        return redirect(url_for('showallproducts'))

 
@app.route('/outofstock',methods=['POST','GET'])
@login_required
def outofstock():
    return render_template('outofstock.html')
 
@app.route('/stock',methods=['POST','GET'])
@login_required
def stock():

     product_snapshot = mongo.db.supplier
     product_snapshot = product_snapshot.find()
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     productSnapShot=[]
     for productStatus in product_snapshot:
        oSnapshot={
                'product_id': productStatus['product_id'],
                'product_name': productStatus['product_name'],
                'product_description': productStatus['product_description'],
                'price_per_qty' : productStatus['price_per_qty'],
                'product_quantity' : int(productStatus['product_quantity']) - int(productStatus['no_orders']),
                'delivery_day' : productStatus['delivery_day']
                }
        avail=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        if avail == 0:
            productSnapShot.append(oSnapshot)

     return json.dumps(productSnapShot)

@app.route('/searchProduct',methods=['POST','GET'])
@login_required
def searchProduct():
    return render_template('searchProduct.html')




@app.route('/bhome')
@login_required
def bhome():
    return render_template('B_Dashboard.html')

@app.route('/shome')
@login_required
def shome():
    return render_template('S_Dashboard.html')

@app.route('/sjob')
@login_required
def sjob():
    return render_template('Search_job.html')


    

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    uname=request.form['username']
    login_user1 = users.find_one({'username' : request.form['username']})
    error = None
    if login_user:
        if request.form['pass'] == login_user1['password']:
            session['username'] = request.form['username']
            session['name']=login_user1['name']
            id = uname.split('user')[-5:]
            user = User(id)
            login_user(user)
            data = {
                'template' : login_user1['partner'],
                'error' : error
                }
    else:
        error = 'Invalid username or password'
        data = {
            'template' : None,
            'error' : error
            }
    return json.dumps(data)
    #return render_template('index.html',error=error)

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['name']})
        error = None
        if existing_user is None:
            name = request.form['name'] 
            partner = request.form['partner']
            uname = name + str(randint(10000,99999))
            if partner == 'B':
                uname = 'B_'+uname
            else:
                uname='S_'+uname
                
            location=request.form['location']
            district=request.form['district']
            pincode=request.form['pincode']
            hashpass=request.form['pincode']
            users.insert({'name' : name, 'username' : uname,'password' : hashpass,'partner' : partner,'location' : location,'district': district,'pincode': pincode})
            params=[uname,hashpass]
            data = {
                'params' : params,
                'error' : error
                }
        else:
            error = 'User Already Exsist !!!'
            data = {
                'params' : None,
                'error' : error
                }
    
    #return render_template('register.html',error=error)
    return json.dumps(data)


@app.route('/orderList',methods=['POST','GET'])
@login_required
def orderList():
    
    return render_template('OrderList.html')
    #return order_status_snapshot
@app.route('/orderList1',methods=['POST','GET'])
@login_required
def orderList1():

     supplier = mongo.db.supplier
     suppliers=supplier.find()
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     supplierList=[]
     for supplier in suppliers:
        available_quantity=int(supplier['product_quantity'])-int(supplier['no_orders'])
        tempSupplier={
                'product_id': supplier['product_id'],
                'product_name': supplier['product_name'],
                'Product_type': supplier['Product_type'],
                'product_description' : supplier['product_description'],
                'price_per_qty' : supplier['price_per_qty'],
                'available_quantity' : available_quantity,
                'delivery_day' : supplier['delivery_day']
                }
        supplierList.append(tempSupplier)

     return json.dumps(supplierList)
@app.route('/placeOrder',methods=['POST','GET'])
@login_required
def placeOrder():
    if request.method == 'POST':
        recievedData = request.json['info']
        order_details = mongo.db.order_details
        supplier=mongo.db.supplier
        user=session['username']
        product_id = recievedData['product_id'] 
        product_name=recievedData['product_name'] 
        price=recievedData['price_per_qty'] 
        order_id=user+str(randint(10000,99999))
        user_id=user   
        now = datetime.datetime.now()
        order_dt= now.strftime("%Y-%m-%d %H:%M")
        thisSupplier = supplier.find_one({'product_id' : product_id})
        try:
            writeResult=order_details.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,'product_name' : product_name, 'price' : price,'quantity' : 1,'delivery_stauts' : 'OG', 'user_id': user_id,'order_dt': order_dt,'supplier_id':thisSupplier['username']})
            if writeResult.inserted_id ==order_id:
            
                no_orders=thisSupplier['no_orders']
                if thisSupplier is not None:
                    result= supplier.update_one({'product_id' : product_id },{"$set" : {'no_orders' : str(int(no_orders)+1)}})
                    if result.modified_count >0:
                       print('if block supplier')
                       return redirect(url_for('orderList'))
                    else:
                       order_details.delete_one({ "_id" : order_id} )
                       print('else block supplier')
                       
                       return result
            else:
                return json.dumps(writeResult) 
        except pymongo.errors.DuplicateKeyError as e:
            print('IN exception')

        
        

@app.route('/orderDetails',methods=['POST','GET'])
@login_required
def orderDetails():
    
    return render_template('orderDetails.html')
    #return order_status_snapshot
@app.route('/showOrderDetails',methods=['POST','GET'])
@login_required
def showOrderDetails():

     order_details = mongo.db.order_details
     user=session['username']
     orders=order_details.find({'user_id' : user})
     print(orders)
     #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     orderList=[]
     for order in orders:
        print(order['product_name'])
        tempOrder={
                'order_id': order['order_id'],
                'product_id': order['product_id'],
                'product_name': order['product_name'],
                'price' : order['price'],
                'quantity' : order['quantity'],
                 'order_dt' : order['order_dt'],
                'delivery_stauts' : order['delivery_stauts']
                }
        orderList.append(tempOrder)
     return json.dumps(orderList)
@app.route('/updateOrder',methods=['POST','GET'])
@login_required
def updateOrder():
    
    return render_template('updateOrder.html')
    #return order_status_snapshot
@app.route('/getOrderData',methods=['POST','GET'])
@login_required
def getOrderData():

     order_details = mongo.db.order_details
     user=session['username']
     orders=order_details.find({'supplier_id' : user})
     print(orders)
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     orderList=[]
     for order in orders:
        print(order['product_name'])
        tempOrder={
                'order_id': order['order_id'],
                'product_id': order['product_id'],
                'product_name': order['product_name'],
                'price' : order['price'],
                'quantity' : order['quantity'],
                 'order_dt' : order['order_dt'],
                'delivery_stauts' : order['delivery_stauts']
                }
        orderList.append(tempOrder)

     return json.dumps(orderList)
    
@app.route('/updateOrderDetails',methods=['POST','GET'])
@login_required
def updateOrderDetails():
    if request.method == 'POST':
        order_details = mongo.db.order_details
        supplier=mongo.db.supplier
        record=request.json['record']
        order_id=record['order_id']
        product_id=record['product_id']
        delivery_stauts=record['delivery_stauts']
        
        thisOrder = order_details.find_one({'order_id' : order_id})
      
        if thisOrder is not None:
          result=order_details.update_one({'order_id' : order_id },{"$set" : {'delivery_stauts' :delivery_stauts }})
          
          if result.modified_count >0: 
              if delivery_stauts == 'DI':
                 thisSupplier = supplier.find_one({'product_id' : product_id})
                 no_orders=thisSupplier['no_orders']
                 result= supplier.update_one({'product_id' : product_id },{"$set" : {'no_orders' : str(int(no_orders)-1)}})
                 print('if block order_details')
                 return redirect(url_for('orderList'))
              
          else:
                  print('else block supplier')
                  return result
        
    return redirect(url_for('updateOrder'))
    
    
@app.route('/completeOrder',methods=['POST','GET'])
@login_required
def completeOrder():
    
    return render_template('completeOrder.html')


@app.route('/getCompleteOrder',methods=['POST','GET'])
@login_required
def getCompleteOrder():

     order_details = mongo.db.order_details
     user=session['username']
     orders=order_details.find({'supplier_id' : user,'delivery_stauts' : 'CO'})
     print(orders)
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     orderList=[]
     for order in orders:
        print(order['product_name'])
        tempOrder={
                'order_id': order['order_id'],
                'product_id': order['product_id'],
                'product_name': order['product_name'],
                'price' : order['price'],
                'quantity' : order['quantity'],
                 'order_dt' : order['order_dt'],
                'delivery_stauts' : order['delivery_stauts']
                }
        orderList.append(tempOrder)

     return json.dumps(orderList)
 
    
if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=5002,host='0.0.0.0')