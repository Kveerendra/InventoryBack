from flask import Flask, render_template, request, session , url_for , redirect,json,Response
from flask_pymongo import PyMongo,pymongo
from flask_cors import CORS
from random import randint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
import datetime
import pandas as pd


app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
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

mongo = PyMongo(app,uri='mongodb://localhost:27017/login_test')

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
    
@app.route('/')
def index():
        return render_template('index.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/create')
@login_required
def create():
    return render_template('B_Success.html')

@app.route('/getProducts',methods=['POST'])
@login_required
def getProducts():
    prodcut_master = mongo.db.prodcut_master
    products_data=prodcut_master.find()
    products=[]
    for product in products_data:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        tempProduct={
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'Product_type': product['Product_type'],
                'product_description': product['product_description'],
                }
        products.append(tempProduct)
    return json.dumps(products)


@app.route('/createproduct' , methods=['GET'])
@login_required
def createproduct():
    return render_template('Add_Product.html')

@app.route('/addproduct', methods=['POST'])
def addproduct():
    if request.method == 'POST':
        supplier = mongo.db.supplier
        
        user=session['username']
        formData=request.json['info']
        product=formData['product']
        form=formData['formData']
        print(product)
        print(form)
        price_per_qty=form['price']
        quantity=form['quantity']
        delivery_day=form['delivery']
        product_id = product["product_id"]
        productname = product['product_name'] 
        Producttype = product['Product_type']  
        description=product['product_description']
        pname=product_id+user
        now = datetime.datetime.now()
        pcreate_dt= now.strftime("%Y-%m-%d %H:%M")
        thisSupplier=supplier.find({'_id':pname})
        if thisSupplier is None:
            supplier.insert({'_id':pname,'product_id':product_id,'product_name' : productname , 'username' : user,'Product_type' : Producttype,'product_description' : description,'price_per_qty' : str(price_per_qty),'product_quantity': str(quantity),'delivery_day': str(delivery_day), 'no_orders': str(0) ,'product_create_dt': pcreate_dt})
        else:
            #new_qty=int(quantity)+thisSupplier['price_per_qty']
            result=supplier.update_one({'_id':pname},{'$set':{'price_per_qty' : str(price_per_qty),'product_quantity': str(quantity),'delivery_day': str(delivery_day)}})
        
        
    return redirect(url_for('createproduct'))
    
@app.route('/showallproducts',methods=['POST','GET'])
@login_required
def showallproducts():
    return render_template('showallproducts.html')

@app.route('/showproducts',methods=['POST','GET'])
@login_required
def showproducts():

     product_snapshot = mongo.db.supplier
     user=session['username']
     product_snapshot = product_snapshot.find({'username' : user})

     productSnapShot=[]
     for productStatus in product_snapshot:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        oSnapshot={
                'product_id': productStatus['product_id'],
                'product_name': productStatus['product_name'],
                'product_description': productStatus['product_description'],
                'price_per_qty' : productStatus['price_per_qty'],
                'product_quantity' :productStatus['product_quantity'],
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
        pname=product_id+user
        print(pname)
        result=supplier.update_one({'_id':pname},{'$set':{'price_per_qty' : price_per_qty,'product_quantity': quantity,'delivery_day': delivery_day,'product_create_dt': pcreate_dt}})
        print(result.modified_count)
        return redirect(url_for('showallproducts'), param=result.modified_count)

 
@app.route('/outofstock',methods=['POST','GET'])
@login_required
def outofstock():
    return render_template('outofstock.html')
 
@app.route('/stock',methods=['POST','GET'])
@login_required
def stock():

     product_snapshot = mongo.db.supplier
     user=session['username']
     product_snapshot = product_snapshot.find({'username' : user })
     
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
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
        #avail= - int(productStatus['no_orders'])
        if  int(productStatus['product_quantity'])== 0:
            productSnapShot.append(oSnapshot)

     return json.dumps(productSnapShot)

@app.route('/searchProduct',methods=['POST','GET'])
@login_required
def searchProduct():
    return render_template('searchProduct.html')


@app.route('/ahome')
@login_required
def ahome():
    return render_template('A_Dashboard.html')


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
    userDetails = request.get_json('userDetails')
    print (userDetails);
    uname = userDetails.get('username')
    login_user1 = users.find_one({'username': userDetails.get('username')})
    error = None
    if login_user1:
        if userDetails.get('password') == login_user1['password']:
            session['username'] = userDetails.get('username')
            session['name']=login_user1['name']
            id = uname.split('user')[-5:]
            user = User(id)
            login_user(user)
#            if login_user1['partner'] == 'A':
##                return render_template('A_Dashboard.html')
#
#            if login_user1['partner'] == 'B':
##                return render_template('orderList.html')
#            else:
##                return render_template('showallproducts.html')
    else:
        error = 'Invalid username or password'

    if login_user1:
        data = {
                    'template' : login_user1['partner'],
                   'error' : error
               }
    else:
        data = {
                    'template' : None,
                   'error' : error
               }
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    return resp
#    return render_template('index.html' , error)
              
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        print (request.files['file'])
        users = mongo.db.users
        f = request.files['file']
        data_xls = pd.read_excel(f)
        user_data_json_array=data_xls.to_json(orient='records')
        parsed = json.loads(user_data_json_array)
        for item in parsed:
            existing_user = users.find_one({'name' : item['name']})
            if existing_user is None:
                users.insert(item)
                print('Inserted : '+ str(item))
            else:
                print('User Already Exsist !!!' + str(item))
        return render_template('excel_upload.html')
    return render_template('excel_upload.html')


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
            return render_template('Register_Sucess.html',params=params)
        else:
            error = 'User Already Exsist !!!'
    
    return render_template('register.html',error=error)


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
        #available_quantity=int(supplier['product_quantity'])-int(supplier['no_orders'])
        tempSupplier={
                'product_id': supplier['product_id'],
                'product_name': supplier['product_name'],
                'Product_type': supplier['Product_type'],
                'product_description' : supplier['product_description'],
                'price_per_qty' : supplier['price_per_qty'],
                'product_quantity' : supplier['product_quantity'],
                'delivery_day' : supplier['delivery_day'],
                'no_orders' : '',
                 's_user_name' : supplier['username']
                }
        supplierList.append(tempSupplier)

     return json.dumps(supplierList)

@app.route('/showWishList',methods=['POST','GET'])
@login_required
def showWishList():
    return render_template('wishListDetails.html')
    #return order_status_snapshot
@app.route('/getWishListData',methods=['POST','GET'])
@login_required
def getWishListData():
     user=session['username']
     wish_list_details = mongo.db.wish_list_details
     wishLists=wish_list_details.find({'sub_contractor_id' : user})
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     wishListData=[]
     for wishes in wishLists:
        #available_quantity=int(supplier['product_quantity'])-int(supplier['no_orders'])
        tempSupplier={
                'wish_id': wishes['wish_id'],
                'product_id': wishes['product_id'],
                'product_name': wishes['product_name'],
                'Product_type' : wishes['Product_type'],
                'price' : wishes['price'],
                'product_quantity' : wishes['quantity'],
                'wish_stauts' : wishes['wish_stauts'],
                'Wisher_id' : wishes['supplier_id'],
                'no_orders' : '',
                # 's_user_name' : wishes['username']
                }
        wishListData.append(tempSupplier)

     return json.dumps(wishListData)

@app.route('/addToWishList',methods=['POST','GET'])
@login_required
def addToWishList():
    if request.method == 'POST':
        recievedData = request.json['info']
        wish_list_details = mongo.db.wish_list_details
        #supplier=mongo.db.supplier
        user=session['username']
        product_id = recievedData['product_id'] 
        product_name=recievedData['product_name'] 
        Product_type=recievedData['Product_type'] 
        product_description=recievedData['product_description'] 
        price=recievedData['price_per_qty'] 
        no_orders=recievedData['no_orders']
        sub_contractor_id=recievedData['s_user_name']
        sub_product_id=product_id+sub_contractor_id
      #  available_quantity=recievedData['available_quantity']
        wish_id=user+str(randint(10000,99999))
        now = datetime.datetime.now()
        order_dt= now.strftime("%Y-%m-%d %H:%M")
        try:
            writeResult=wish_list_details.insert_one({'_id' : wish_id ,'wish_id':wish_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : '',
                                                          'product_name' : product_name,'Product_type' : Product_type,
                                                          'product_description' : product_description, 
                                                          'price' : str(price),
                                                          'quantity' : str(no_orders),
                                                          'wish_stauts' : 'PE',
                                                          'wish_dt': order_dt,'supplier_id':user,'sub_contractor_id' : sub_contractor_id})
            return redirect(url_for('subcontract'))
        except pymongo.errors.DuplicateKeyError as e:
            print('IN exception')
@app.route('/placeOrder',methods=['POST','GET'])
@login_required
def placeOrder():
    if request.method == 'POST':
        recievedData = request.json['info']
        order_details_staging = mongo.db.order_details_staging
        #supplier=mongo.db.supplier
        user=session['username']
        product_id = recievedData['product_id'] 
        product_name=recievedData['product_name'] 
        Product_type=recievedData['Product_type'] 
        product_description=recievedData['product_description'] 
        price=recievedData['price_per_qty'] 
        no_orders=recievedData['no_orders']
        sub_contractor_id=recievedData['s_user_name']
        sub_product_id=product_id+sub_contractor_id
      #  available_quantity=recievedData['available_quantity']
        order_id=user+str(randint(10000,99999))
        now = datetime.datetime.now()
        order_dt= now.strftime("%Y-%m-%d %H:%M")
        try:
            writeResult=order_details_staging.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : '',
                                                          'product_name' : product_name,'Product_type' : Product_type,
                                                          'product_description' : product_description, 
                                                          'price' : str(price),
                                                          'quantity' : str(no_orders),
                                                          'delivery_stauts' : 'OG',
                                                          'order_dt': order_dt,'supplier_id':user,'sub_contractor_id' : sub_contractor_id})
            return redirect(url_for('subcontract'))
        except pymongo.errors.DuplicateKeyError as e:
            print('IN exception')

@app.route('/placeOrderSupplier',methods=['POST','GET'])
@login_required
def placeOrderSupplier():
    if request.method == 'POST':
        recievedData = request.json['info']
        order_details_staging = mongo.db.order_details_staging
        #supplier=mongo.db.supplier
        supplier_id  =session['username']
        product_id = recievedData['product_id'] 
        product_name=recievedData['product_name'] 
        Product_type=recievedData['Product_type'] 
        product_description=recievedData['product_description'] 
        price=recievedData['price_per_qty'] 
        no_orders=recievedData['no_orders']
        sub_contractor_id=recievedData['s_user_name']
        #available_quantity=recievedData['product_quantity']
        order_id=supplier_id+str(randint(10000,99999))
         
        now = datetime.datetime.now()
        order_dt= now.strftime("%Y-%m-%d %H:%M")
        sub_product_id=product_id+sub_contractor_id
        sup_product_id=product_id+supplier_id
        try:
            writeResult=order_details_staging.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : sup_product_id,
                                                          'product_name' : product_name,'Product_type' : Product_type,
                                                          'product_description' : product_description, 
                                                          'price' : str(price),
                                                          'quantity' : str(no_orders),
                                                          'delivery_stauts' : 'OG',
                                                          'order_dt': order_dt,'supplier_id':supplier_id,'sub_contractor_id' : sub_contractor_id})
            return redirect(url_for('subcontract'))
        except pymongo.errors.DuplicateKeyError as e:
            print('IN exception')
        
        
@app.route('/myOrders',methods=['POST','GET'])
@login_required
def myOrders():
    return render_template('myOrders.html')


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
 
@app.route('/getMySubcontractors',methods=['POST','GET'])
@login_required
def getMySubcontractors():
    
    return render_template('mySubContractors.html')
    #return order_status_snapshot
@app.route('/getContractorsData',methods=['POST','GET'])
@login_required
def getContractorsData():

     sub_contracotor_details = mongo.db.sub_contracotor_details
     user=session['username']
     contracotors=sub_contracotor_details.find({'supplier_id' : user})
     print(contracotors)
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     contracotorList=[]
     for contracotor in contracotors:
        
        tempOrder={
                'sub_contractor_id' : contracotor['sub_contractor_id'],
                'product_id' : contracotor['product_id'],
                'product_name': contracotor['product_name'],
                'price' : contracotor['price'],
                'quantity' : contracotor['ordered_quantity'],
                 'order_dt' : contracotor['order_dt'],
                'delivery_stauts' : contracotor['delivery_stauts']
                }
        contracotorList.append(tempOrder)

     return json.dumps(contracotorList)    
@app.route('/updateOrder',methods=['POST','GET'])
@login_required
def updateOrder():
    
    return render_template('updateOrder.html')
    #return order_status_snapshot
@app.route('/getOrderData',methods=['POST','GET'])
@login_required
def getOrderData():

     order_details_staging = mongo.db.order_details_staging
     user=session['username']
     orders=order_details_staging.find({'sub_contractor_id' : user})
     print(orders)
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     orderList=[]
     for order in orders:
        print(order['product_name'])
        tempOrder={
                'order_id': order['order_id'],
                'product_id': order['product_id'],
                'sub_product_id': order['sub_product_id'],
                'sup_product_id': order['sup_product_id'],
                'product_name': order['product_name'],
                'price' : order['price'],
                'Product_type' : order['Product_type'],
                'quantity' : order['quantity'],
                'product_description' : order['product_description'],
                'order_dt' : order['order_dt'],
                'delivery_stauts' : order['delivery_stauts'],
                'supplier_id' : order['supplier_id'],
                'sub_contractor_id' : order['sub_contractor_id']
                }
        orderList.append(tempOrder)

     return json.dumps(orderList)
    
@app.route('/updateOrderDetails',methods=['POST','GET'])
@login_required
def updateOrderDetails():
    if request.method == 'POST':
        order_details = mongo.db.order_details
        order_history = mongo.db.order_history
        order_details_staging=mongo.db.order_details_staging
        sub_contracotor_details=mongo.db.sub_contracotor_details
        supplier=mongo.db.supplier
        record=request.json['record']
        order_id=record['order_id']
        product_id=record['product_id']
        product_name=record['product_name']
        sup_product_id=record['sup_product_id']
        sub_product_id=record['sub_product_id']
        Product_type = record['Product_type']
        product_description = record['product_description']
        price=record['price']
        order_dt=record['order_dt']
        delivery_stauts=record['delivery_stauts']
        supplier_id=record['supplier_id']
        sub_contractor_id=record['sub_contractor_id']
        ordered_quantity=record['quantity']
        print(ordered_quantity)
        
        thisOrder = order_details.find_one({'order_id' : order_id})
        
        thisSubContractor = supplier.find_one({'_id' : sub_product_id})
        
        if thisOrder is None:
            if delivery_stauts == 'CO':
                writeResult=order_details.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : sup_product_id,
                                                          'product_name' : product_name,
                                                          'price' : str(price),
                                                          'quantity' : ordered_quantity,
                                                          'delivery_stauts' : delivery_stauts,
                                                          'order_dt': order_dt,
                                                          'supplier_id':supplier_id,
                                                          'sub_contractor_id' : sub_contractor_id})
                writeResult=order_history.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : sup_product_id,
                                                          'product_name' : product_name,
                                                          'price' : str(price),
                                                          'quantity' : ordered_quantity,
                                                          'delivery_stauts' : delivery_stauts,
                                                          'order_dt': order_dt,
                                                          'supplier_id':supplier_id,
                                                          'sub_contractor_id' : sub_contractor_id})
                order_details_staging.delete_one({'_id' : order_id})
                if order_id[0] =='S':
                    print("In suppliers order")
                   # supplier_id=thisOrder['user_id']
                    print(supplier_id)
                    print(product_id)
                    thisSupplier = supplier.find_one({'_id' : sup_product_id})
                    sub_id=supplier_id+sub_contractor_id+product_id
                    print(sub_id)
                    thisSubcontracotor=sub_contracotor_details.find_one({'_id' : sub_id})
                    if thisSubcontracotor is not None :
                        print("Exist")
                        sub_contracotor_details.update_one({'_id' : sub_id },{"$set" : {'ordered_quantity' : str(int(thisSubcontracotor['ordered_quantity'])+int(ordered_quantity))}})
                    else:
                        print("new")
                        sub_contracotor_details.insert_one({'_id' : sub_id,'sub_contractor_id' : sub_contractor_id,'supplier_id' : supplier_id,'product_id' : product_id,'product_name' : product_name,'ordered_quantity' : ordered_quantity,'price' : price,'delivery_stauts' : delivery_stauts,'order_dt': order_dt,})
                    if thisSupplier is not  None:
                        print("Product found updating existing")
                        new_sup_qty=int(ordered_quantity)+int(thisSupplier['product_quantity'])
                        result=supplier.update_one({'_id' : sup_product_id },{"$set" : {'product_quantity' : str(new_sup_qty)}})
                        
                        new_sub_qty=int(thisSubContractor['product_quantity'])-int(ordered_quantity)
                        if new_sub_qty <0:
                            new_sub_qty=0;
                        result=supplier.update_one({'_id' : sub_product_id },{"$set" : {'product_quantity' : str(new_sub_qty)}})
                        
                    else:
                        print("New Record----")
                        supplier.insert_one({'_id' : sup_product_id,'product_id' : product_id,'product_name' : product_name,'username' : supplier_id,'Product_type' : Product_type,'product_description' : product_description,'price_per_qty' : price,'product_quantity' : ordered_quantity,'delivery_day' : '1','no_orders' : '0','product_create_dt' : order_dt})
                        new_sub_qty=int(thisSubContractor['product_quantity'])-int(ordered_quantity)
                        if new_sub_qty <0:
                            new_sub_qty=0;
                        result=supplier.update_one({'_id' : sub_product_id },{"$set" : {'product_quantity' : str(new_sub_qty)}})
                else:
                        print("New Record----1")
                        new_sub_qty=int(thisSubContractor['product_quantity'])-int(ordered_quantity)
                        if new_sub_qty <0:
                            new_sub_qty=0;
                        result=supplier.update_one({'_id' : sub_product_id },{"$set" : {'product_quantity' : str(new_sub_qty)}})
                   
            else:
                 print("New Record----2")
                 if order_id[0] =='S':
                     sub_id=supplier_id+sub_contractor_id+product_id
                     thisSubcontracotor=sub_contracotor_details.find_one({'_id' : sub_id})
                     if thisSubcontracotor is not None :
                        print("Exist")
                        sub_contracotor_details.update_one({'_id' : sub_id },{"$set" : {'ordered_quantity' : str(int(thisSubcontracotor['ordered_quantity'])+int(ordered_quantity))}})
                     else:
                        print("new")
                        sub_contracotor_details.insert_one({'_id' : sub_id,'sub_contractor_id' : sub_contractor_id,'supplier_id' : supplier_id,'product_id' : product_id,'product_name' : product_name,'ordered_quantity' : ordered_quantity,'price' : price,'delivery_stauts' : delivery_stauts,'order_dt': order_dt,})
                    
                 writeResult=order_history.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : sup_product_id,
                                                          'product_name' : product_name,
                                                          'price' : str(price),
                                                          'quantity' : ordered_quantity,
                                                          'delivery_stauts' : delivery_stauts,
                                                          'order_dt': order_dt,
                                                          'supplier_id':supplier_id,
                                                          'sub_contractor_id' : sub_contractor_id})
                 writeResult=order_details.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : sup_product_id,
                                                          'product_name' : product_name,
                                                          'price' : str(price),
                                                          'quantity' : ordered_quantity,
                                                          'delivery_stauts' : delivery_stauts,
                                                          'order_dt': order_dt,
                                                          'supplier_id':supplier_id,
                                                          'sub_contractor_id' : sub_contractor_id})
                 order_details_staging.delete_one({'_id' : order_id})
                

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
 
@app.route('/getStock',methods=['POST','GET'])
@login_required
def getStock():
     supplier = mongo.db.supplier
     user=session['username']
     print(user)
     productinfo=request.json['info']
     print(productinfo)
     product_snapshot = supplier.find({'username': { '$ne': user}})
     print(product_snapshot)

     productSnapShot=[]
     for productStatus in product_snapshot:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        if productStatus['product_id'] == productinfo['product_id']:
            oSnapshot={
                    'product_id': productStatus['product_id'],
                    'product_name': productStatus['product_name'],
                    'subcontractor_id' : productStatus['username'],
                    'product_description': productStatus['product_description'],
                    'Product_type' :  productStatus['Product_type'],
                    'price_per_qty' : productStatus['price_per_qty'],
                    'product_quantity' :productStatus['product_quantity'],
                    'delivery_day' : productStatus['delivery_day'],
                    'no_orders' : '',
                    's_user_name' : productStatus['username'],
                    'supplier_product_id' : productinfo['product_id']
                    }
            productSnapShot.append(oSnapshot)
     print(productSnapShot)
     return json.dumps(productSnapShot)
    
@app.route('/placeOrderToSuContractor',methods=['POST','GET'])
@login_required
def placeOrderToSuContractor():
    if request.method == 'POST':
        order_details = mongo.db.order_details
        supplier_col=mongo.db.supplier
        productDetails=request.json['info']
        sub_product_id=productDetails['product_id']
        supplier_product_id=productDetails['supplier_product_id']
        product_name=productDetails['product_name']
        subcontractor_id=productDetails['subcontractor_id']
        price_per_qty=productDetails['price_per_qty']
        product_quantity=productDetails['product_quantity']
        no_orders=productDetails['no_orders']
        supplier_id=productDetails['supplier_id']
        order_id=supplier_id+str(randint(10000,99999))
        now = datetime.datetime.now()
        order_dt= now.strftime("%Y-%m-%d %H:%M")
        
        supplier = supplier_col.find_one({'product_id' : supplier_product_id})
        subContractor = supplier_col.find_one({'product_id' : sub_product_id})
        new_no_orders=str(int(subContractor['no_orders'])+ int(no_orders))
        new_sub_qty=int(product_quantity)-int(no_orders)
        new_sup_qut=int(no_orders)+int(supplier['product_quantity'])
        if new_sub_qty < 0:
            new_sub_qty=0
        try:
           writeResult=order_details.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':sub_product_id,'product_name' : product_name, 'price' : str(price_per_qty),'quantity' : str(no_orders),'delivery_stauts' : 'OG', 'user_id': supplier_id,'order_dt': order_dt,'supplier_id':subContractor['username']})
           return redirect(url_for('outofstock'))  
           #if writeResult.inserted_id ==order_id: 
            #   if supplier is not None:
             #      result= supplier_col.update({'product_id' : supplier_product_id },{ "$set": {'product_quantity' : str(new_sup_qut) }})
              # if subContractor is not None:
               #    result= supplier_col.update({'product_id' : sub_product_id },{"$set": {'no_orders' : new_no_orders , 'product_quantity' : str(new_sub_qty) }})
                         
                           
             
          # else:
           #     return json.dumps(writeResult) 
        except pymongo.errors.DuplicateKeyError as e:
            print('IN exception')
        return redirect(url_for('outofstock')) 
    
    
@app.route('/subcontract',methods=['POST','GET'])
@login_required
def subcontract():
    
    return render_template('SubContract.html')


@app.route('/orderList2',methods=['POST','GET'])
@login_required
def orderList2():

     supplier = mongo.db.supplier
     user=session['username']
     suppliers=supplier.find({'username': { '$ne': user}})
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     supplierList=[]
     for supplier in suppliers:
       # available_quantity=int(supplier['product_quantity'])-int(supplier['no_orders'])
        tempSupplier={
                'product_id': supplier['product_id'],
                'product_name': supplier['product_name'],
                'Product_type': supplier['Product_type'],
                'product_description' : supplier['product_description'],
                'price_per_qty' : supplier['price_per_qty'],
                'product_quantity' : supplier['product_quantity'],
                'delivery_day' : supplier['delivery_day'],
                'no_orders' : '',
                's_user_name' : supplier['username']
                }
        supplierList.append(tempSupplier)

     return json.dumps(supplierList)

@app.route('/pendingOrders',methods=['POST','GET'])
@login_required
def pendingOrders():
    
    return render_template('pendingOrders.html')

@app.route('/pendingOrdersBuyer',methods=['POST','GET'])
@login_required
def pendingOrdersBuyer():
    
    return render_template('pendingOrdersBuyer.html')

@app.route('/getPendingData',methods=['POST','GET'])
@login_required
def getPendingData():

     order_details_staging = mongo.db.order_details_staging
     user=session['username']
     orders=order_details_staging.find({'supplier_id' : user})
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

@app.route('/createMasterData' , methods=['GET'])
@login_required
def createMasterData():
    return render_template('addMasterProduct.html')
@app.route('/insertMasterData', methods=['POST'])
def insertMasterData():
    if request.method == 'POST':
        prodcut_master = mongo.db.prodcut_master
        data=request.json['info']
        productname = data['productname'] 
        pname = productname+'_'+str(randint(10000,99999))
        Producttype = data['Producttype']  
        description=data['description']
        prodcut_master.insert({'_id':pname,'product_id':pname,'product_name' : productname ,'Product_type' : Producttype,'product_description' : description})
        
        
    return redirect(url_for('createMasterData'))


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=5002,host='0.0.0.0')