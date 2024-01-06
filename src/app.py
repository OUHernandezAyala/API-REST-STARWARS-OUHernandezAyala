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
        new_people = People(name=data["name"], 
                            birth_year = data["birth_year"], 
                            gender = data["gender"], 
                            planet_origin = data["planet_origin"], 
                            description = data["description"], 
                            url_img_people = data["url_img_people"], 
                            species = data["species"] )
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
    

@app.route('/planets', methods=['POST','GET'])
def handle_planets():
    data = request.json
    revision_data = [data.get("name")]
    if request.method == 'POST':
        planet_exist = Planets.query.filter_by(name=data["name"]).one_or_none()
        if planet_exist:
            return jsonify({"message":"The planet alredy exist"}), 400
        print("Hola",planet_exist)
        if None in revision_data:
            return jsonify({"message":"name required"}), 400
        #VERIFICAR QUE EL CORREO NO EXITA EN LA BASE DE DATOS
        new_planet = Planets(name=data["name"],
                                          type=data["type"],  
                                          terrain=data["terrain"],  
                                          diameter=data["diameter"],  
                                          description=data["description"],
                                          url_img_planet=data["url_img_planet"],  
                                        )
        try:
            db.session.add(new_planet)
            db.session.commit()
        except Exception as error:
            print(error)
            return jsonify({"message":"Server error, try again"}), 400
        print(new_planet)
        return jsonify(data), 201
    if request.method == 'GET':
        all_planets = Planets.query.all()
        planets_serialized = []
        for planet in all_planets:
            planets_serialized.append(planet.serialize())
        print(planets_serialized)
        return jsonify(planets_serialized), 200

@app.route('/user/<int:user_id>/favorites/<string:type>', methods=['POST', 'GET', 'DELETE'])
def handle_favorites_for_user(user_id, type):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User doesn't exist"}), 404

    if request.method == 'POST':
        data = request.json
        if not ("type" in data and ("people_id" in data or "planets_id" in data)):
            return jsonify({"message": "Missing required fields"}), 400
        valid_types = ["people", "planets"]
        if type not in valid_types:
            return jsonify({"message": "Invalid 'type'"}), 400

        favorite_exist_people = None
        favorite_exist_planet = None

        if "people_id" in data:
            favorite_exist_people = Favorites.query.filter_by(user_id=user_id, people_id=data["people_id"]).one_or_none()

        if "planets_id" in data:
            favorite_exist_planet = Favorites.query.filter_by(user_id=user_id, planets_id=data["planets_id"]).one_or_none()

        print("favorite_exist_people:", favorite_exist_people)
        print("favorite_exist_planet:", favorite_exist_planet)


        if favorite_exist_people or favorite_exist_planet:
            return jsonify({"message": "Favorite already exists"}), 400

        new_favorite = Favorites(
            user_id=user_id,
            type=type,
            people_id=data.get("people_id"),  
            planets_id=data.get("planets_id") 
        )

        try:
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify(new_favorite.serialize()), 201
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"message": "Server error, try again"}), 500

    elif request.method == 'GET':
        all_favorites = Favorites.query.filter_by(user_id=user_id).all()
        favorites_serialized = [favorite.serialize() for favorite in all_favorites]
        return jsonify(favorites_serialized), 200
    
    elif request.method == 'DELETE':
         data = request.json
         if not ("type" in data and ("people_id" in data or "planets_id" in data)):
            return jsonify({"message": "Missing required fields"}), 400
         valid_types = ["people", "planets"]
         if type not in valid_types:
                return jsonify({"message": "Invalid 'type'"}), 400
         
         favorite_exist_people = None
         favorite_exist_planet = None
         if "people_id" in data:
                favorite_exist_people = Favorites.query.filter_by(user_id=user_id, people_id=data["people_id"]).one_or_none()
         if "planets_id" in data:
                favorite_exist_planet = Favorites.query.filter_by(user_id=user_id, planets_id=data["planets_id"]).one_or_none()

         if not (favorite_exist_people or favorite_exist_planet):
                return jsonify({"message": "Favorite does not exist"}), 404

         try:
            db.session.delete(favorite_exist_people or favorite_exist_planet)
            db.session.commit()
            return jsonify({"message": "Favorite deleted successfully"}), 200
         except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify({"message": "Server error, try again"}), 500


@app.route('/<string:type>/<int:id>', methods=['GET'])
def handle_one_type(type,id):
    if request.method == 'GET':
        if type == "planets":
            planet = Planets.query.filter_by(id=id).first()
            if planet:
                try:
                    return jsonify(planet.serialize()), 200
                except Exception as error:
                    print(error)
                    return jsonify({"message": "Server error, try again"}), 500
            else:
                return jsonify({"message": "Planet not found"}), 404
        elif type == "people":
            people = People.query.filter_by(id=id).first()
            if people:
                try:
                    return jsonify(people.serialize()), 200
                except Exception as error:
                    print(error)
                    return jsonify({"message": "Server error, try again"}), 500
            else:
                return jsonify({"message": "People not found"}), 404
    else:
        return jsonify({"message": "Method not allowed"}), 400


