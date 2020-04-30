import os
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_cors import CORS
from pymongo import MongoClient
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
cors = CORS(app, resouse={
    r"/*": {
        "origins": "*"
    }
})

UPLOAD_FOLDER = './path/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'zip'}

#database mongo as cache
clientMongo = MongoClient('localhost',port=27017)
dbMongo = clientMongo["BUSINESS"] #la crea si no esta creada


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_paas.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type_id = db.Column(db.Integer, nullable=False)
    manager_id = db.Column(db.Integer, nullable=False)
    num_modules = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return '<Business %r>' % self.name

class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(10), nullable=False)
    business_id = db.Column(db.Integer, nullable=False)

class Business_type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    def __rep__(self):
        return '<Business_type %r>' % self.name

class Managers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return '<Managers %r>' % self.name

class Modules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.String(200), default=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return '<Modules %r>' % self.name

class Purchased_modules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, nullable=False)
    business_id = db.Column(db.Integer, nullable=False)
    is_activate = db.Column(db.Integer, default=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return '<Purchased_modules %r>' % self.id

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(200), nullable=False)
    last_update = db.Column(db.String(200), default=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return '<Template %r>' % self.id



@app.route('/')
def index():
    return render_template('index.html')


#devuelve el detalle de la empresa
@app.route('/api/business/<int:id>', methods=['GET'])
def call_business_detail():
    return "call_business_detail"

#verifica a usuarios
@app.route('/api/auth', methods=['POST'])
def call_auth():
    if request.method == 'POST':
        res = request.json
        print(res)
        data = Auth.query.filter_by(name=res["user"])
        user = data.user
        password = data.password

        if(res["pass"] == password):
            print("LOGIN ACCESS")

            business = Business.query.filter_by(id=data.business_id)

            modules = []
            col = dbMongo[business.name]
            #documentos = modulos (plugins)
            for module in col.find({}):
                print(module)
                modules.append(module)

            resp = business.__dict__
            del resp['_sa_instance_state'] #elimina valor
            resp["created"] = str(resp["created"]) #convierte valor datetime a string
            resp["modules"] = module

            print("\n\nRESULT - ", "call_auth","\n",resp, "\n\n")
            return jsonify(data=resp)

        
    return "ERROR REQUEST"

#devuelve datos de configuración



#devuelve la lista de las empresas asociadas
#agrega una nueva empresa
@app.route('/api/business', methods=['GET','POST'])
def call_business():
    if request.method == 'GET':
        data = Business.query.order_by(Business.created).all()
        r = []
        #print(data[0].name)
        for business in data:
            d = business.__dict__
            del d['_sa_instance_state'] #elimina valor
            d["created"] = str(d["created"]) #convierte valor datetime a string
            r.append(d)
        print("\n\nRESULT - ", "call_business_list","\n",r, "\n\n")
        return jsonify(data=r)

    elif request.method == 'POST':
        res = request.json
        print(res)

        #verify if exists
        data_verify_not_repeat = Business.query.filter_by(name=res["name"])
        if data_verify_not_repeat.first() is not None:
            return jsonify(result="BUSINESS EXITED")

        manager = res["manager"]
        data_manager =Managers(
            name=manager["name"], 
            last_name=manager["lastName"],
            phone=manager["phone"],
            email=manager["email"])

        try:
            db.session.add(data_manager)
            #db.session.commit()
            print('SAVE SUCCESS MANAGER')
        except:
            print("SAVE ERROR MANAGER")

        db_manager = Managers.query.order_by(Managers.created).all()
        
        data_business = Business(
            name=res["name"], 
            type_id=res["type_id"],
            manager_id=db_manager[-1].id)

        data_auth = Auth(
            user=res["user"],
            password=res["pass"]
        )
        
        try:
            db.session.add(data_business)
            db.session.add(data_auth)
            db.session.commit()
            return jsonify(result="SAVE SUCCESS")
        except:
            return jsonify(result="SAVE ERROR")

    return "ERROR REQUEST"

#devuelve la lista de modulos por empresa
@app.route('/api/business/modules/<int:b_id>', methods=['GET', 'POST'])
def call_business_list_modules(b_id):
    if request.method == 'GET':
        data = Purchased_modules.query.filter_by(business_id=b_id)
        r = []
        #print(data[0].name)
        for module in data:
            d = module.__dict__
            del d['_sa_instance_state'] #elimina valor
            d["created"] = str(d["created"]) #convierte valor datetime a string
            r.append(d)
        print("\n\nRESULT - ", "call_purchased_modules","\n",r, "\n\n")
        return jsonify(data=r)

    elif request.method == 'POST':
        res = request.json
        print(res)

         #verify if business has module
        data_verify_not_repeat = Purchased_modules.query.filter_by(business_id=res["business_id"],module_id=res["module_id"])
        if data_verify_not_repeat.first() is not None:
            return jsonify(result="BUSINESS HAS MODULE")
        
        data = Purchased_modules(
            module_id=res["module_id"],
            business_id=res["business_id"],)

        #update business data
        data_business = Business.query.filter_by(id=res["business_id"]).first()
        data_business.num_modules += 1

        #get data module
        data_module = Modules.query.filter_by(id=res["module_id"]).first()

        #add module in cache database
        col = dbMongo[data_business.name]
        col.insert_one({
            "name": data_module.name,
            "buy_date": "12-12-20",
        })

        '''col.insert_many([
            {
            "name": "registro",
            "buy_date": "12-08-20",
            },
            {
                "name": "registro",
                "buy_date": "12-08-20",
            }
        ])'''

        print(clientMongo.list_database_names())
        print(dbMongo.list_collection_names())
        #print(col.count_documents())

        try:
            db.session.add(data_business)
            db.session.add(data)
            db.session.commit()
            return jsonify(result="SAVE SUCCESS")
        except:
            return jsonify(result="SAVE ERROR MODULE BUSINESS")

        
    return "ERROR REQUEST"

#devuelve la lista de modulos existentes
#agrega un nuevo modulo
@app.route('/api/modules', methods=['GET','POST'])
def call_modules():

    if request.method == 'GET':
        data = Modules.query.all()
        r = []
        #print(data[0].name)
        for module in data:
            d = module.__dict__
            del d['_sa_instance_state'] #elimina valor
            d["last_update"] = str(d["last_update"])
            d["created"] = str(d["created"]) #convierte valor datetime a string
            r.append(d)
        print("\n\nRESULT - ", "call_modules","\n",r, "\n\n")
        return jsonify(data=r)

    elif request.method == 'POST':
        res = request.json
        print(res)

        #verify if exists
        data_verify_not_repeat = Modules.query.filter_by(name=res["name"])
        if data_verify_not_repeat.first() is not None:
            return jsonify(result="MODULE EXITED")
        
        data =Modules(
            name=res["name"],
            status=res["status"])

        try:
            db.session.add(data)
            db.session.commit()
            return jsonify(result="SAVE SUCCESS")
        except:
            return jsonify(result="SAVE ERROR MODULE")

        
    return "ERROR REQUEST"

#devuelve el detalle del modulo
@app.route('/api/modules/<int:id>', methods=['GET'])
def call_modules_detail():
    return "call_modules_detail"

#devuelve la lista de plantillas de estilos
@app.route('/api/template', methods=['GET', 'POST'])
def call_template():
    if request.method == 'GET':
        data = Template.query.all()
        r = []
        #print(data[0].name)
        for template in data:
            d = template.__dict__
            del d['_sa_instance_state'] #elimina valor
            d["last_update"] = str(d["last_update"])
            d["created"] = str(d["created"]) #convierte valor datetime a string
            r.append(d)
        print("\n\nRESULT - ", "call_template","\n",r, "\n\n")
        return jsonify(data=r)

    elif request.method == 'POST':
        res = request.json
        print(res)
        
        data =Template(
            name=res["name"],
            status=res["status"])

        try:
            db.session.add(data)
            db.session.commit()
            return jsonify(result="SAVE SUCCESS")
        except:
            return jsonify(result="SAVE ERROR TEMPLATE")

        
    return "ERROR REQUEST"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/modules/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print(file.filename)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        print(file.filename)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file',filename=filename))
            return jsonify(result="SAVE FILE")

    return jsonify(data='''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    ''')


if __name__ == "__main__":
    app.run(debug=True)