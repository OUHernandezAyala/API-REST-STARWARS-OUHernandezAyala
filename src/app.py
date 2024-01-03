"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
# ACEDEMOS AL .env EN BUSCA DE DATABASE_URL
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['POST','GET'])
def handle_user():
    data = request.json
    revision_data = [data.get("email"), data.get("password"), data.get("name")]
    if request.method == 'POST':
        user_exist = User.query.filter_by(email=data["email"]).one_or_none()
        if user_exist:
            return jsonify({"message":"email alredy exist"}), 400
        print("Hola",user_exist)
        if None in revision_data:
            return jsonify({"message":"email,password and name required"}), 400
        #VERIFICAR QUE EL CORREO NO EXITA EN LA BASE DE DATOS
        new_user = User(email=data["email"],password=data["password"], name=data["name"] )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as error:
            print(error)
            return jsonify({"message":"Server error, try again"}), 400
        print(new_user)
        return jsonify(data), 201
    if request.method == 'GET':
        all_user = User.query.all()
        user_serialized = []
        for user in all_user:
            user_serialized.append(user.serialize())
        print(user_serialized)
        return jsonify(user_serialized), 200
        

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
