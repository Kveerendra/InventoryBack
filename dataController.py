
from flask import Flask, render_template, request, session , url_for , redirect,json
from flask_pymongo import PyMongo,pymongo
from random import randint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from flask_cors import CORS
import datetime


app = Flask(__name__)
CORS(app)
app.config.update(
    DEBUG = True
)


#app.config['MONGO_DBNAME'] = 'IMO'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/IMO'

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
        data=request.get_json(force=True).get('info')
        user=request.get_json(force=True).get('user')
        print(data)
        productname = data['product_name']
        product_id = data['product_id']
        pname = product_id+user['username']
        product_type = data['product_type']  
        description=data['product_description']
        product_price=data['product_price']
        quantity=data['product_quantity']
        delivery_day=data['product_delivery']
        now = datetime.datetime.now()
        pcreate_dt= now.strftime("%Y-%m-%d %H:%M")
        thisSupplier=supplier.find_one({'_id':pname})
        action=''
        if thisSupplier is None:
            action='Inserted'
            supplier.insert_one({'_id':pname,'product_id':product_id,'product_name' : productname , 'username' : user['username'],'product_type' : product_type, 'product_description' : description, 'product_price' : product_price,'product_quantity': quantity,'delivery_day': delivery_day, 'no_orders': 0 ,'product_create_dt': pcreate_dt})
        else:
            action='Updated'
            supplier.update_one({'product_id':product_id},{'$set':{'product_price' : product_price,'product_quantity': str(int(quantity)+int(thisSupplier['product_quantity'])),'delivery_day': delivery_day,'product_create_dt': pcreate_dt}})
        return json.dumps(action)	
        
    #return redirect(url_for('createproduct'))
    
@app.route('/showallproducts',methods=['POST','GET'])
@login_required
def showallproducts():
    return render_template('showallproducts.html')

@app.route('/showproducts',methods=['POST','GET'])
def showproducts():

     product_snapshot = mongo.db.supplier
     product_snapshot = product_snapshot.find()

     productSnapShot=[]
     for productStatus in product_snapshot:
        qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        oSnapshot={
                'product_id': productStatus['product_id'],
                'product_name': productStatus['product_name'],
                'product_price' : productStatus['product_price'],
                'product_description' : productStatus['product_description'],
                'product_quantity' :qty,
                'delivery_day' : productStatus['delivery_day'],
                'product_type' : productStatus['product_type'],
                's_user_name' : productStatus['username']
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
                'product_price' : productStatus['product_price'],
                                                          'product_quantity' : productStatus['product_quantity'],
                                                          'delivery_day' : productStatus['delivery_day']
                }
        productSnapShot.append(oSnapshot)
     return json.dumps(productSnapShot)
              
@app.route('/updateProduct',methods=['POST'])
def updateProduct():
    if request.method == 'POST':
        supplier = mongo.db.supplier
        user=request.get_json(force=True).get('user')
        productinfo=request.get_json(force=True).get('info')
        product_name = productinfo['product_name'] 
        product_id=productinfo['product_id']
        product_price=productinfo['product_price']
        quantity=productinfo['product_quantity']
        delivery_day=productinfo['delivery_day']
        now = datetime.datetime.now()
        pcreate_dt= now.strftime("%Y-%m-%d %H:%M")
        print(delivery_day)
        supplier.update_one({'product_id':product_id},{'$set':{'product_name' : product_name , 'username' : user['username'],'product_price' : product_price,'product_quantity': quantity,'delivery_day': delivery_day,'product_create_dt': pcreate_dt}})
        formData = {
		        'product_id': product_id,
                'product_name': product_name,
			    'username': user['username'],
                'product_price': product_price,
                'product_quantity': quantity,
                'delivery_day': delivery_day,
			    'product_create_dt': pcreate_dt
                        };  
        data = {
                    'info' : formData,
		    'error' : None
					
               } 
        return json.dumps(data)
	#return redirect(url_for('showallproducts'))

 
@app.route('/outofstock',methods=['POST','GET'])
@login_required
def outofstock():
    return render_template('outofstock.html')
 
@app.route('/stock',methods=['GET'])
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
                'product_price' : productStatus['product_price'],
                'product_quantity' : int(productStatus['product_quantity']) - int(productStatus['no_orders']),
                'delivery_day' : productStatus['delivery_day'],
                'product_type' : productStatus['product_type'],
                's_user_name' : productStatus['username']
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
    uname=request.get_json(force=True).get('username') #request.form['username'] #(request.get_json(force=True).get('username')
    login_user1 = users.find_one({'username' : uname})
    error = None
    if login_user1:
        if request.get_json(force=True).get('password') == login_user1['password']:
            session['username'] = request.get_json(force=True).get('username')
            session['name']=login_user1['name']
            id = uname.split('user')[-5:]
            user = User(id)
            login_user(user)
            role=''
            if login_user1['partner'] == 'B':
                role='buyer'
            else:
                if login_user1['partner'] == 'S':
                    role='seller'
            data = {
                    'username' : login_user1['username'],
                    'role' : role,
                    'error' : error
            }
        else:
            error = 'Invalid username or password'
            data  = {
                    'template' : None,
                   'error' : error
                }
    else:
        error = 'Invalid username or password'
        data  = {
                    'template' : None,
                   'error' : error
            }
    print(data)
    return json.dumps(data)
    #return render_template('index.html',error=error)

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.get_json(force=True).get('name')})
        error = None
        if existing_user is None:
            name = request.get_json(force=True).get('name')
            partner = request.get_json(force=True).get('partner')
            uname = name + str(randint(10000,99999))
            if partner == 'B':
                uname = 'B_'+uname
            else:
                uname='S_'+uname
                
            location=request.get_json(force=True).get('location') #request.form['location']
            district=request.get_json(force=True).get('district') #request.form['district']
            pincode=request.get_json(force=True).get('pincode') #request.form['pincode']
            hashpass=request.get_json(force=True).get('pincode') #request.form['pincode']
            users.insert_one({'name' : name, 'username' : uname,'password' : hashpass,'partner' : partner,'location' : location,'district': district,'pincode': pincode})
            params=[uname,hashpass]
            #return render_template('Register_Sucess.html',params=params)
            data = {
                    'params' : params,
		    'error' : error
            }
        else:
            error = 'User Already Exsist !!!'
            data  = {
                    'params' : None,
		    'error' : error
            }
    
    #return render_template('register.html',error=error)
    return json.dumps(data)

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
                users.insert_one(item)
                data = {
		             'existing_user' : existing_user,
			     'item' : str(item)
		       }
            else:
                data = {
			      'existing_user' : existing_user,
			      'item' : str(item)
		       }
    return json.dumps(data)
        #return render_template('excel_upload.html')
    #return render_template('excel_upload.html')

@app.route("/aupload", methods=['GET', 'POST'])
def aupload():
    if request.method == 'POST':
        print (request.files['file'])
        product_master = mongo.db.product_master
        f = request.files['file']
        data_xls = pd.read_excel(f)
        user_data_json_array=data_xls.to_json(orient='records')
        parsed = json.loads(user_data_json_array)
        for item in parsed:
            print(item)
            existing_user =product_master.find_one({'product_id': item['product_id']})
            if existing_user is None:
                product_master.insert_one(item)
                data = {
			      'existing_user' : existing_user,
			      'item' : str(item)
		       }
            else:
                data = {
			      'existing_user' : existing_user,
			      'item' : str(item)
		       }
    return json.dumps(data)
        #return render_template('excel_aupload.html')
    #return render_template('excel_aupload.html')

@app.route('/addToWishList',methods=['POST','GET'])
#@login_required #updatepoduct, upload, aupload, addtowhishlist
def addToWishList():
    if request.method == 'POST':
        recievedData = request.get_json(force=True).get('product') 
        wish_list_details = mongo.db.wish_list_details
        #supplier=mongo.db.supplier
        userInfo=request.get_json(force=True).get('userInfo')
        user = userInfo['username']
        product_id = recievedData['product_id'] 
        product_name=recievedData['product_name'] 
        product_type=recievedData['product_type'] 
        product_description=recievedData['product_description'] 
        product_price=recievedData['product_price'] 
        no_orders=recievedData['quantity_ordered']
        sub_contractor_id=recievedData['s_user_name']
        sub_product_id=product_id+sub_contractor_id
      #  available_quantity=recievedData['available_quantity']
        wish_id=user+product_id
        now = datetime.datetime.now()
        order_date= now.strftime("%Y-%m-%d %H:%M")
        wish_list_detail=wish_list_details.find_one({'wish_id' : wish_id})
        print(wish_list_detail)
        try:
            if wish_list_detail is not None:
                quantity=int(wish_list_detail['quantity'])+int(no_orders)
                wish_list_details.update_one({'_id' : wish_list_detail['wish_id'] },{"$set" : {'quantity' : str(quantity)}})
                data = {
			      '_id' : wish_list_detail['wish_id'],
			      'quantity' : str(quantity)
		        }
                #return redirect(url_for('subcontract'))
            else:
                wish_list_details.insert_one({'_id' : wish_id ,'wish_id':wish_id,'product_id':product_id,
                                                          'sub_product_id' : sub_product_id,'sup_product_id' : '',
                                                          'product_name' : product_name,'product_type' : product_type,
                                                          'product_description' : product_description, 
                                                          'product_price' : str(product_price),
                                                          'quantity' : str(no_orders),
                                                          'wish_stauts' : 'PE',
                                                          'wish_dt': order_date,'supplier_id':user,'sub_contractor_id' : sub_contractor_id})
                wish_list_detail=wish_list_details.find_one({'wish_id' : wish_id})
                data = {
			       '_id' : wish_list_detail['wish_id'],
				'wish_id':wish_id,
				'product_id':product_id,
                                'sub_product_id' : sub_product_id,
				'sup_product_id' : '',
                                'product_name' : product_name,
				'product_type' : product_type,
                                'product_description' : product_description, 
                                'product_price' : str(product_price),
                                'quantity' : str(no_orders),
                                'wish_stauts' : 'PE',
                                'wish_dt': order_date,
				'supplier_id':user,
				'sub_contractor_id' : sub_contractor_id
			    }
                #return redirect(url_for('subcontract'))
            return json.dumps(data)   
        except pymongo.errors.DuplicateKeyError as e:
            print('IN exception')
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
                'product_type': supplier['product_type'],
                'product_description' : supplier['product_description'],
                'product_price' : supplier['product_price'],
                'available_quantity' : available_quantity,
                'delivery_day' : supplier['delivery_day']
                }
        supplierList.append(tempSupplier)

     return json.dumps(supplierList)
# @app.route('/placeOrder',methods=['POST','GET'])
# @login_required
# def placeOrder():
#     if request.method == 'POST':
#         recievedData = request.json['info']
#         order_details = mongo.db.order_details
#         supplier=mongo.db.supplier
#         user=session['username']
#         product_id = recievedData['product_id']
#         product_name=recievedData['product_name']
#         price=recievedData['product_price']
#         order_id=user+str(randint(10000,99999))
#         user_id=user
#         now = datetime.datetime.now()
#         order_date= now.strftime("%Y-%m-%d %H:%M")
#         thisSupplier = supplier.find_one({'product_id' : product_id})
#         try:
#             writeResult=order_details.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,'product_name' : product_name, 'price' : price,'quantity' : 1,'delivery_stauts' : 'OG', 'user_id': user_id,'order_date': order_date,'supplier_id':thisSupplier['username']})
#             if writeResult.inserted_id ==order_id:
#
#                 no_orders=thisSupplier['no_orders']
#                 if thisSupplier is not None:
#                     result= supplier.update_one({'product_id' : product_id },{"$set" : {'no_orders' : str(int(no_orders)+1)}})
#                     if result.modified_count >0:
#                        print('if block supplier')
#                        return redirect(url_for('orderList'))
#                     else:
#                        order_details.delete_one({ "_id" : order_id} )
#                        print('else block supplier')
#
#                        return result
#             else:
#                 return json.dumps(writeResult)
#         except pymongo.errors.DuplicateKeyError as e:
#             print('IN exception')
#To get the order status
@app.route('/getOrderStatus',methods=['POST','GET'])
def getOrderStatus():
    if request.method == 'POST':
        order_details = mongo.db.order_details
        recievedData = request.get_json(force=True).get('info')
        sub_contractor_id = recievedData['sub_contractor_id']
        orders = order_details.find({'sub_contractor_id': sub_contractor_id})
@app.route('/placeOrder',methods=['POST'])
def placeOrder():
    if request.method == 'POST':
        recievedData = request.get_json(force=True).get('info') 
        order_details_staging = mongo.db.order_details_staging
        sub_contracotor_details=mongo.db.supplier
        #supplier=mongo.db.supplier
        #user=session['username']
        #_id = recievedData['_id']
        product_id = recievedData['product_id']
        product_name=recievedData['product_name']
        product_type=recievedData['product_type']
        product_description=recievedData['product_description']
        product_price=recievedData['product_price']
        no_orders=recievedData['product_quantity']
        new_order=recievedData['quantity_ordered']
        #sub_contractor_id=recievedData['username']
        supplier_id=recievedData['username']
        #supplier_id = ' '
        sub_contractor_id=recievedData['s_user_name'] #Added-Snigdha
        sub_product_id=product_id+sub_contractor_id
        product_quantity=recievedData['product_quantity']
        order_id=supplier_id+str(randint(10000,99999))
        now = datetime.datetime.now()
        order_date= now.strftime("%Y-%m-%d %H:%M")
        #thisSubContractor = sub_contracotor_details.find_one({'_id' : _id})
        thisSubContractor = sub_contracotor_details.find_one({'_id' :sub_product_id})
        available_quantity = thisSubContractor['no_orders']
        #print(thisSubContractor)
        try:
            writeResult=order_details_staging.insert_one({'_id' : order_id ,'order_id':order_id,'product_id':product_id,
                                                            'sub_product_id' : sub_product_id,'sup_product_id' : '',
                                                            'product_name' : product_name,'product_type' : product_type,
                                                            'product_description' : product_description,
                                                            'product_price' : str(product_price),
                                                            'quantity' : str(new_order),
                                                            'delivery_stauts' : 'OG',
                                                            'order_date': order_date,'supplier_id':supplier_id,'sub_contractor_id' : sub_contractor_id})
            order=int(new_order)+int(thisSubContractor['no_orders'])
    
                    #return redirect(url_for('subcontract'))
    
            #result=sub_contracotor_details.update_one({'_id': _id}, {"$set": {'no_orders': str(order)}})
            result=sub_contracotor_details.update_one({'_id': sub_product_id}, {"$set": {'no_orders': str(order)}})
            if result.modified_count > 0:
                data = {
                        'product_id': product_id,
                        'product_name': product_name,
                        'product_type': product_type,
                        'product_description': product_description,
                        'product_price': product_price,
                            #'no_orders': available_quantity - new_order,
    			        'no_orders': order,
                        'new_order': new_order,
    		            'user': sub_contractor_id,
                        'delivery_stauts' : 'OG',
                        'flag' : 'success'
                        }
            else :
                data = {
                        'product_id': product_id,
                        'product_name': product_name,
                        'product_type': product_type,
                        'product_description': product_description,
                        'product_price': product_price,
                        'no_orders': available_quantity,
                        'new_order': new_order,
    		            'user' : sub_contractor_id,
                        'delivery_stauts' : 'OG',
                        'flag' : 'error'
                        }
            return json.dumps(data)
        except pymongo.errors.DuplicateKeyError as e:
            print('IN exception')

        
        

@app.route('/orderDetails',methods=['POST','GET'])
@login_required
def orderDetails():
    
    return render_template('orderDetails.html')
    #return order_status_snapshot
#show all details for a supplier
@app.route('/showOrderDetails',methods=['POST','GET'])
def showOrderDetails():

     order_details_staging = mongo.db.order_details_staging
     order_details = mongo.db.order_details
     user=request.get_json(force=True).get('username')
     orders=order_details_staging.find({'supplier_id' : user})
     ordersDetail=order_details.find({'supplier_id' : user})
     print(user)
     #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     
     orderList=[]
     for order in orders:
        print(order['product_name'])
        tempOrder={
                'order_id': order['order_id'],
                'product_id': order['product_id'],
                'product_name': order['product_name'],
                'product_price' : order['product_price'],
                'quantity_ordered' : order['quantity'],
                'order_date' : order['order_date'],
                'delivery_stauts' : order['delivery_stauts'],
                'supplier_id' : user,
                's_user_name' : order['sub_contractor_id'],
                'sub_product_id' : order['product_id'] + order['sub_contractor_id'],
                'sup_product_id' : order['product_id'] + order['supplier_id'],
                'product_type' : order['product_type'],
                'product_description' : order['product_type']
                }
        orderList.append(tempOrder)
     for ordr in ordersDetail:
        temp={
                'order_id': ordr['order_id'],
                'product_id': ordr['product_id'],
                'product_name': ordr['product_name'],
                'product_price' : ordr['product_price'],
                'quantity_ordered' : ordr['quantity'],
                'order_date' : ordr['order_date'],
                'delivery_stauts' : ordr['delivery_stauts'],
                'supplier_id' : user,
                's_user_name' : ordr['sub_contractor_id'],
                'sub_product_id' : ordr['product_id'] + ordr['sub_contractor_id'],
                'sup_product_id' : ordr['product_id'] + ordr['supplier_id'],
                'product_type' : ordr['product_type'],
                'product_description' : ordr['product_type']
                }
        orderList.append(temp)
     return json.dumps(orderList)
#show pending orders
@app.route('/showOrderPendingForApproval',methods=['POST'])
def showOrderPendingForApproval():

     order_details_staging = mongo.db.order_details_staging
     print(request)
     user=request.get_json(force=True).get('username')
     orders=order_details_staging.find({'sub_contractor_id' : user, 'delivery_stauts': 'OG'})
     print(user)
     #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     orderList=[]
     for order in orders:
        print(order['product_name'])
        tempOrder={
                #'s_user_name':order['sub_contractor_id'],
                's_user_name': order['sub_contractor_id'],
                'product_id': order['product_id'],
                'product_name': order['product_name'],
                'product_price' : order['product_price'],
                'quantity_ordered' : order['quantity'],
                'order_date' : order['order_date'],
                'delivery_stauts' : order['delivery_stauts'],
                'order_id': order['order_id'],
                'product_type' : order['product_type'],
                'product_description' : order['product_description'],
                'sub_product_id' : order['product_id'] + order['sub_contractor_id'],
                'sup_product_id' : order['product_id'] + order['supplier_id'],
                'supplier_id' : order['supplier_id']

                }
        orderList.append(tempOrder)
     return json.dumps(orderList)
@app.route('/updateOrder',methods=['POST','GET'])
@login_required
def updateOrder():
    
    return render_template('updateOrder.html')
    #return order_status_snapshot
@app.route('/getOrderData',methods=['POST','GET'])
def getOrderData():

     order_details = mongo.db.order_details
     user=request.get_json(force=True).get('username')
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
                'product_price' : order['product_price'],
                'quantity' : order['quantity'],
                'order_date' : order['order_date'],
                'delivery_stauts' : order['delivery_stauts']
                }
        orderList.append(tempOrder)

     return json.dumps(orderList)
    
# @app.route('/updateOrderDetails',methods=['POST','GET'])
# @login_required
# def updateOrderDetails():
#     if request.method == 'POST':
#         order_details = mongo.db.order_details
#         supplier=mongo.db.supplier
#         record=request.json['record']
#         order_id=record['order_id']
#         product_id=record['product_id']
#         delivery_stauts=record['delivery_stauts']
#
#         thisOrder = order_details.find_one({'order_id' : order_id})
#
#         if thisOrder is not None:
#           result=order_details.update_one({'order_id' : order_id },{"$set" : {'delivery_stauts' :delivery_stauts }})
#
#           if result.modified_count >0:
#               if delivery_stauts == 'DI':
#                  thisSupplier = supplier.find_one({'product_id' : product_id})
#                  no_orders=thisSupplier['no_orders']
#                  result= supplier.update_one({'product_id' : product_id },{"$set" : {'no_orders' : str(int(no_orders)-1)}})
#                  print('if block order_details')
#                  return redirect(url_for('orderList'))
#
#           else:
#                   print('else block supplier')
#                   return result
#
#     return redirect(url_for('updateOrder'))
@app.route('/updateOrderDetails1', methods=['POST'])
def updateOrderDetailsDummy():
    userInfo=request.get_json(force=True).get('userInfo')
    print(userInfo)
    productRecord=request.get_json(force=True).get('productRecord')
    #productRecord['delivery_stauts'] would be 'Decline' or 'Approved'
    print(productRecord)


@app.route('/updateOrderDetails', methods=['POST'])
def updateOrderDetails():
    if request.method == 'POST':
        order_details = mongo.db.order_details
        order_history = mongo.db.order_history
        order_details_staging = mongo.db.order_details_staging
        sub_contracotor_details = mongo.db.sub_contracotor_details
        supplier = mongo.db.supplier
        record = request.get_json(force=True).get('productRecord')
        order_id = record['order_id']
        product_id = record['product_id']
        product_name = record['product_name']
        sup_product_id = record['sup_product_id']
        sub_product_id = record['sub_product_id']
        product_type = record['product_type']
        product_description = record['product_description']
        product_price = record['product_price']
        order_date = record['order_date']
        delivery_stauts = record['delivery_stauts']
        supplier_id = record['supplier_id']
        sub_contractor_id = record['s_user_name']
        ordered_quantity = record['quantity_ordered']
        print(delivery_stauts)

        thisOrder = order_details_staging.find_one({'order_id': order_id})
        print(order_id)

        thisSubContractor = supplier.find_one({'_id': sub_product_id})
        print(sub_product_id)
        sup_product_id=product_id+supplier_id
        

        if thisOrder is not None:
            if delivery_stauts == 'CO':
                writeResult = order_details.insert_one({'_id': order_id, 'order_id': order_id, 'product_id': product_id,
                                                        'sub_product_id': sub_product_id,
                                                        'sup_product_id': sup_product_id,
                                                        'product_name': product_name,
                                                        'product_price': str(product_price),
                                                        'quantity': ordered_quantity,
                                                        'product_type' : product_type,
                                                        'delivery_stauts': delivery_stauts,
                                                        'order_date': order_date,
                                                        'supplier_id': supplier_id,
                                                        'sub_contractor_id': sub_contractor_id})
                writeResult = order_history.insert_one({'_id': order_id, 'order_id': order_id, 'product_id': product_id,
                                                        'sub_product_id': sub_product_id,
                                                        'sup_product_id': sup_product_id,
                                                        'product_name': product_name,
                                                        'product_price': str(product_price),
                                                        'product_type' : product_type,
                                                        'quantity': ordered_quantity,
                                                        'delivery_stauts': delivery_stauts,
                                                        'order_date': order_date,
                                                        'supplier_id': supplier_id,
                                                        'sub_contractor_id': sub_contractor_id})
                order_details_staging.delete_one({'_id': order_id})
                if order_id[0] == 'S':
                    print("In suppliers order")
                    # supplier_id=thisOrder['user_id']
                    print(supplier_id)
                    print(product_id)
                    thisSupplier = supplier.find_one({'_id': sup_product_id})
                    sub_id = supplier_id + sub_contractor_id + product_id
                    print(sub_id)
                    thisSubcontracotor = sub_contracotor_details.find_one({'_id': sub_id})
                    if thisSubcontracotor is not None:
                        print("Updating subcontractor to sub_contractor_details ")
                        sub_contracotor_details.update_one({'_id': sub_id}, {"$set": {'ordered_quantity': str(
                            int(thisSubcontracotor['ordered_quantity']) + int(ordered_quantity))}})

                    else:
                        print("Adding new subcontractor to sub_contractor_details")
                        sub_contracotor_details.insert_one(
                            {'_id': sub_id, 'sub_contractor_id': sub_contractor_id, 'supplier_id': supplier_id,
                             'product_id': product_id, 'product_name': product_name,
                             'ordered_quantity': ordered_quantity, 'product_price': product_price, 'delivery_stauts': delivery_stauts,
                             'order_date': order_date, })
                    if thisSupplier is not None:
                        print("Product found updating existing")
                        new_sup_qty = int(ordered_quantity) + int(thisSupplier['product_quantity'])
                        result = supplier.update_one({'_id': thisSupplier['_id']},
                                                     {"$set": {'product_quantity': str(new_sup_qty)}})

                        new_sub_qty = int(thisSubContractor['product_quantity']) - int(ordered_quantity)
                        if new_sub_qty < 0:
                            new_sub_qty = 0;
                        result = supplier.update_one({'_id': sub_product_id},
                                                     {"$set": {'product_quantity': str(new_sub_qty)}})
                        new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                        supplier.update_one({'_id': sub_product_id}, {"$set": {'no_orders': str(new_order)}})
                    else:
                        print("New Record----")
                        supplier.insert_one(
                            {'_id': sup_product_id, 'product_id': product_id, 'product_name': product_name,
                             'username': supplier_id, 'product_type': product_type,
                             'product_description': product_description, 'product_price': product_price,
                             'product_quantity': ordered_quantity, 'delivery_day': '1', 'no_orders': '0',
                             'product_create_dt': order_date})
                        new_sub_qty = int(thisSubContractor['product_quantity']) - int(ordered_quantity)
                        if new_sub_qty < 0:
                            new_sub_qty = 0;
                        result = supplier.update_one({'_id': thisSubContractor['_id']},
                                                     {"$set": {'product_quantity': str(new_sub_qty)}})
                        new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                        supplier.update_one({'_id': thisSubContractor['_id']}, {"$set": {'no_orders': str(new_order)}})
                else:
                    print("New Record----1 this block is for buyer place an order to supplier and supplier approves ")
                    new_sub_qty = int(thisSubContractor['product_quantity']) - int(ordered_quantity)
                    print(new_sub_qty)
                    print(product_id)
                    if new_sub_qty < 0:
                        new_sub_qty = 0;
                    result = supplier.update_one({'_id': thisSubContractor['_id']},
                                                 {"$set": {'product_quantity': str(new_sub_qty)}})
                    new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                    supplier.update_one({'_id': thisSubContractor['_id']}, {"$set": {'no_orders': str(new_order)}})

            else:
                print(
                    "New Record----2 for this block is for buyer/supplier place an order to supplier and supplier Denied ")
                print(order_id[0])
                if order_id[0] == 'S':
                    sub_id = supplier_id + sub_contractor_id + product_id
                    thisSubcontracotor = sub_contracotor_details.find_one({'_id': sub_id})
                    
                    if thisSubcontracotor is not None:
                        print("Exist")
                        sub_contracotor_details.update_one({'_id': sub_id}, {"$set": {'ordered_quantity': str(
                            int(thisSubcontracotor['ordered_quantity']) + int(ordered_quantity))}})
                        #new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                        #supplier.update_one({'_id': sub_product_id}, {"$set": {'no_orders': str(new_order)}})
                        new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                        supplier.update_one({'_id': thisSubContractor['_id']}, {"$set": {'no_orders': str(new_order)}})
                    else:
                        print("new")
                        sub_contracotor_details.insert_one(
                            {'_id': sub_id, 'sub_contractor_id': sub_contractor_id, 'supplier_id': supplier_id,
                             'product_id': product_id, 'product_name': product_name,
                             'ordered_quantity': ordered_quantity, 'product_price': product_price, 'delivery_stauts': delivery_stauts,
                             'order_date': order_date, })
                        new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                        supplier.update_one({'_id': thisSubContractor['_id']}, {"$set": {'no_orders': str(new_order)}})
                else:
                    print("This will execute for buyer declined orders")
                #new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                #supplier.update_one({'_id': sub_product_id}, {"$set": {'no_orders': new_order}})
                    new_order = int(thisSubContractor['no_orders']) - int(ordered_quantity)
                    supplier.update_one({'_id': thisSubContractor['_id']}, {"$set": {'no_orders': str(new_order)}})
                writeResult = order_history.insert_one({'_id': order_id, 'order_id': order_id, 'product_id': product_id,
                                                        'sub_product_id': sub_product_id,
                                                        'sup_product_id': sup_product_id,
                                                        'product_name': product_name,
                                                        'product_price': str(product_price),
                                                        'product_type' : product_type,
                                                        'quantity': ordered_quantity,
                                                        'delivery_stauts': delivery_stauts,
                                                        'order_date': order_date,
                                                        'supplier_id': supplier_id,
                                                        'sub_contractor_id': sub_contractor_id})
                writeResult = order_details.insert_one({'_id': order_id, 'order_id': order_id, 'product_id': product_id,
                                                        'sub_product_id': sub_product_id,
                                                        'sup_product_id': sup_product_id,
                                                        'product_name': product_name,
                                                        'product_price': str(product_price),
                                                        'product_type' : product_type,
                                                        'quantity': ordered_quantity,
                                                        'delivery_stauts': delivery_stauts,
                                                        'order_date': order_date,
                                                        'supplier_id': supplier_id,
                                                        'sub_contractor_id': sub_contractor_id})
                order_details_staging.delete_one({'_id': order_id})

    data = {
        'order_id': order_id,
        'product_id': product_id,
        'product_name': product_name,
        'product_price': product_price,
        'quantity': ordered_quantity,
        'order_date': order_date,
        'delivery_stauts': delivery_stauts
    }
    return json.dumps(data)
    # return redirect(url_for('updateOrder'))        
    
    
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
                'product_price' : order['product_price'],
                'quantity' : order['quantity'],
                 'order_date' : order['order_date'],
                'delivery_stauts' : order['delivery_stauts']
                }
        orderList.append(tempOrder)

     return json.dumps(orderList)
 
@app.route('/productList',methods=['GET'])
def getProducts():
    product_master = mongo.db.product_master
    products_data=product_master.find()
    products=[]
    for product in products_data:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        tempProduct={
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'product_type': product['product_type'],
                'product_description': product['product_description'],
                }
        products.append(tempProduct)
    return json.dumps(products)

@app.route('/insertMasterData', methods=['POST'])
def insertMasterData():
    if request.method == 'POST':
        product_master = mongo.db.product_master
        data=request.get_json(force=True).get('info')
        productname = data['product_name'] 
        pname = productname+'_'+str(randint(10000,99999))
        Producttype = data['product_type']  
        description=data['product_description']
        product_master.insert_one({'_id':pname,'product_id':pname,'product_name' : productname ,'product_type' : Producttype,'product_description' : description})
        
        
    return getProducts

@app.route('/getWishList', methods=['POST'])
def getWishList():
    userInfo=request.get_json(force=True).get('userInfo')
    wish_list_details = mongo.db.wish_list_details
    print(userInfo['username'])
    wish_list_detail=wish_list_details.find({"sub_contractor_id" : userInfo['username']})
    retObj =[]
    for product in wish_list_detail:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        tempProduct={
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'product_type': product['product_type'],
                'product_description': product['product_description'],
                'product_price':product['product_price'],
                'product_quantity':product['quantity'],
                'wish_status': product['wish_stauts'],
                'wisher_id':product['wish_id']
                }
        print(tempProduct)
        retObj.append(tempProduct)
    print(retObj)
    return json.dumps(retObj)

@app.route('/getMyOutOfStockProducts', methods=['POST'])
def getMyOutOfStockProducts():
    userInfo=request.get_json(force=True).get('userInfo')
    supplier = mongo.db.supplier
    products_data=supplier.find({"username" :userInfo['username'],"product_quantity":0})
    products=[]
    for product in products_data:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        tempProduct={
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'product_type': product['product_type'],
                'product_description': product['product_description'],
                'product_price': product['product_price'],
                'product_quantity': product['product_quantity'],
                'delivery_day': product['delivery_day']
                }
        products.append(tempProduct)
    return json.dumps(products)


@app.route('/getAvailableSubContractorsForProduct', methods=['POST'])
def getAvailableSubContractorsForProduct():
    userInfo=request.get_json(force=True).get('userInfo')
    product=request.get_json(force=True).get('product')
    supplier = mongo.db.supplier
    products_data=supplier.find({"product_type":product["product_type"],"username" :{"$ne": userInfo['username']},"product_quantity":{"$ne": 0}})
    products=[]
    for product in products_data:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        tempProduct={
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'product_type': product['product_type'],
                'product_description': product['product_description'],
                'product_price': product['product_price'],
                'product_quantity': product['product_quantity'],
                'delivery_day': product['delivery_day'],
                's_user_name': product['username']
                }
        products.append(tempProduct)
    return json.dumps(products)

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=5003,host='0.0.0.0')
