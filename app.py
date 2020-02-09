from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_paas.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type_id = db.Column(db.Integer, nullable=False)
    manager_id = db.Column(db.Integer, nullable=False)
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
    last_update = db.Column(db.String(200), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return '<Modules %r>' % self.name

class Purchased_modules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, nullable=False)
    business_id = db.Column(db.Integer, nullable=False)
    is_activate = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __rep__(self):
        return '<Purchased_modules %r>' % self.id




@app.route('/')
def index():
    return render_template('index.html')

#devuelve la lista de las empresas asociadas
@app.route('/api/business/list', methods=['GET'])
def call_business_list():
    data = Business.query.order_by(Business.created).all()
    r = []
    #print(data[0].name)
    for business in data:
        d = business.__dict__
        del d['_sa_instance_state'] #elimina valor
        d["created"] = str(d["created"]) #convierte valor datetime a string
        r.append(d)
    print("\n\nRESULT - ", "call_business_list","\n",r, "\n\n")
    return json.dumps(r)

#devuelve el detalle de la empresa
@app.route('/api/business/detail/<int:id>', methods=['GET'])
def call_business_detail():
    return "call_business_detail"

#agrega una nueva empresa
@app.route('/api/business/add', methods=['POST'])
def call_business_add():
    if request.method == 'POST':
        res = request.json
        print(res)

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
            type_id=0,
            manager_id=db_manager[-1].id)
        
        try:
            db.session.add(data)
            db.session.commit()
            return jsonify(result="SAVE SUCCESS")
        except:
            return jsonify(result="SAVE ERROR")

    return "ERROR REQUEST"

#devuelve la lista de modulos por empresa
@app.route('/api/business/list_modules/<int:id>', methods=['GET'])
def call_business_list_modules():
    return "call_business_list_modules"

#devuelve la lista de modulos existentes
@app.route('/api/modules/list', methods=['GET'])
def call_modules_list():
    return "call_modules_list"

#devuelve el detalle del modulo
@app.route('/api/modules/detail/<int:id>', methods=['GET'])
def call_modules_detail():
    return "call_modules_detail"

#devuelve la lista de plantillas de estilos
@app.route('/api/template/list', methods=['GET'])
def call_template_list():
    return "call_template_list"


if __name__ == "__main__":
    app.run(debug=True)