from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
cors = CORS(app, resouse={
    r"/*": {
        "origins": "*"
    }
})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_paas.db'
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
        
        data = Business(
            name=res["name"], 
            type_id=res["type_id"],
            manager_id=db_manager[-1].id)
        
        try:
            db.session.add(data)
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
        update_business = Business.query.filter_by(id=res["business_id"]).first()
        update_business.num_modules += 1

        try:
            db.session.add(update_business)
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


if __name__ == "__main__":
    app.run(debug=True)