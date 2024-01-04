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
from models import db, User, Favorites, People, Planets
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

@app.route('/people', methods=['POST','GET'])
def handle_people():
    data = request.json
    revision_data = [data.get("name")]
    if request.method == 'POST':
        people_exist = People.query.filter_by(name=data["name"]).one_or_none()
        if people_exist:
            return jsonify({"message":"Character alredy exist"}), 400
        print("Hola",people_exist)
        if None in revision_data:
            return jsonify({"message":"name required"}), 400
        #VERIFICAR QUE EL CORREO NO EXITA EN LA BASE DE DATOS
        new_people = People(name=data["name"], birth_year = data["birth_year"], gender = data["gender"], planet_origin = data["planet_origin"], description = data["description"], url_img_people = data["url_img_people"], species = data["species"] )
        try:
            db.session.add(new_people)
            db.session.commit()
        except Exception as error:
            print(error)
            return jsonify({"message":"Server error, try again"}), 400
        print(new_people)
        return jsonify(data), 201
    if request.method == 'GET':
        all_people = People.query.all()
        people_serialized = []
        for people in all_people:
            people_serialized.append(people.serialize())
        print(people_serialized)
        return jsonify(people_serialized), 200
    


@app.route('/user/<int:user_id>/favorites', methods=['POST','GET'])
def handle_favorites(user_id):
     user = User.query.get(user_id)
     if user is None:
         return jsonify({ "message": "User dont exist"}), 404
     data = request.json
     revision_data = [data.get("type")]
     favorite_exist_people = Favorites.query.filter_by(user= data["user_id"], people_id = data["people_id"]).one_or_none()
     favorite_exist_planet = Favorites.query.filter_by(user= data["user_id"], planets_id = data["planets_id"]).one_or_none()
     if request.method == 'POST':
        if favorite_exist_planet:
            return jsonify({"message":"Planet Favorite alredy exist"}), 400
            print("Hola",favorite_exist_planet)
        if favorite_exist_people:
            return jsonify({"message":"People Favorite alredy exist"}), 400
            print("Hola",favorite_exist_people)
        if None in revision_data:
            return jsonify({"message":"Type is required"}), 400
        #VERIFICAR QUE EL FAVORITO NO EXITA EN LA BASE DE DATOS
        new_favorite = Favorites(type=type)
        try:
            print('hola', new_favorite)
        except Exception as error:
            print(error)
            return jsonify({"message":"Server error, try again"}), 400
        print(new_favorite)
        return jsonify(data), 201
     if request.method == 'GET':
        all_Favorites = Favorites.query.all()
        
        

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
