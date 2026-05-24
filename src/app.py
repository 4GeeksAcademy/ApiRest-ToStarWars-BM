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
from models import db, User, People, Planet, Favorite, Vehicle
from sqlalchemy import select
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

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

@app.route('/people', methods=['GET'])
def get_all_peoples():
    result_all_people = db.session.execute(select(People)).scalars().all()
    return jsonify([people.serialize() for people in result_all_people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    character = db.session.get(People, people_id)
    if character is None:
        return jsonify({"msg": "personaje no encontrado"}), 404
    return jsonify(character.serialize()),200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    result_all_planets = db.session.execute(select(Planet)).scalars().all()
    return jsonify([planet.serialize() for planet in result_all_planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planets_id(planet_id):
    planet = db.session.get(Planet, planet_id)
    if planet is None:
        return jsonify({"msg": "planeta no encontrado"}), 404
    return jsonify(planet.serialize()),200

@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = db.session.execute(select(User)).scalars().all()
    return jsonify([user.serialize() for user in all_users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_users_favorites():
    users_favorites = db.session.execute(select(Favorite).where(Favorite.user_id == 1)).scalars().all()
    return jsonify ([fav.serialize()for fav in users_favorites]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id): 
    planet_exists = db.session.get(Planet, planet_id)
    if planet_exists is None:
        return jsonify({"msg": "El planeta que intentas agregar no existe"}), 404 
    new_favorito= Favorite(
         user_id= 1,
         planet_id= planet_id,
    )
    db.session.add(new_favorito)
    db.session.commit()
    return jsonify (new_favorito.serialize()),200

@app.route ('/favorite/people/<int:people_id>', methods=['POST'])
def add_people_favorite(people_id):
    people_exists = db.session.get(People, people_id)
    if people_exists is None:
        return jsonify({"msg": "El personaje que intentas agregar no existe"}), 404
    new_people_favorite= Favorite(
        user_id= 1,
        people_id= people_id,
    )
    db.session.add(new_people_favorite)
    db.session.commit()
    return jsonify(new_people_favorite.serialize()), 200

@app.route ('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    
    planet_to_delete = db.session.execute(select(Favorite).where(Favorite.planet_id == planet_id, Favorite.user_id==1)).scalar_one_or_none()
    if planet_to_delete is None:
        return jsonify({"msg": "Favorito no existe"}), 404
    
    db.session.delete(planet_to_delete)
    db.session.commit()
    return jsonify({"msg": "Eliminado con exito"}), 200

@app.route ('/favorite/people/<int:people_id>', methods=['DELETE'])
def people_delete(people_id):
    people_to_delete= db.session.execute(select(Favorite).where(Favorite.people_id==people_id, Favorite.user_id==1)).scalar_one_or_none()
    if people_to_delete is None:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(people_to_delete)
    db.session.commit()
    return jsonify ({"msg": "Eliminado con exito"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
