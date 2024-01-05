from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model): #PARENT
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    favorites = relationship("Favorites", back_populates="user")
    

    def __repr__(self):
        return '<UserURIEL %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email
            # do not serialize the password, its a security breach
        }
    
class Favorites(db.Model): #CHILD
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", back_populates="favorites")
    type = db.Column(db.String(120), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"))
    people = relationship("People", back_populates="favorites")
    planets_id = db.Column(db.Integer, db.ForeignKey("planets.id"))
    planets = relationship("Planets", back_populates="favorites")

    def __repr__(self):
        return f'<Favorites {self.id}, Type: {self.type}>'

class People(db.Model): #PARENT 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    birth_year = db.Column(db.String(10))
    gender = db.Column(db.String(50))
    planet_origin = db.Column(db.String(100))
    description = db.Column(db.String(100))
    url_img_people = db.Column(db.String(300))
    species  = db.Column(db.String(100))
    favorites = relationship("Favorites", back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "planet_origin": self.planet_origin,
            "description": self.description,
            "url_img_people": self.url_img_people,
            "species": self.species
        }


class Planets(db.Model): #PARENT 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    type = db.Column(db.String(150))
    terrain  = db.Column(db.String(100))
    diameter  = db.Column(db.String(100))
    description = db.Column(db.String(200))
    url_img_planet = db.Column(db.String(300))
    favorites = relationship("Favorites", back_populates="planets")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "terrain": self.terrain,
            "diameter": self.diameter,
            "description": self.description,
            "url_img_planet": self.url_img_planet,
        }

    