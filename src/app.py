import os
from flask import Flask, request, jsonify
from models import db, User, People, Planet, FavoritePlanet, FavoritePeople

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/people', methods=['GET'])
def get_all_people():
    people_list = People.query.all()
    return jsonify([p.serialize() for p in people_list]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets_list = Planet.query.all()
    return jsonify([p.serialize() for p in planets_list]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1 
    fav_planets = FavoritePlanet.query.filter_by(user_id=current_user_id).all()
    fav_people = FavoritePeople.query.filter_by(user_id=current_user_id).all()
    return jsonify({
        "planets": [p.serialize() for p in fav_planets],
        "people": [pe.serialize() for pe in fav_people]
    }), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1
    if not Planet.query.get(planet_id):
        return jsonify({"msg": "El planeta no existe"}), 404
    exists = FavoritePlanet.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if exists:
        return jsonify({"msg": "Ya se encuentra en tus favoritos"}), 400
    new_fav = FavoritePlanet(user_id=current_user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Planeta agregado a favoritos"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    current_user_id = 1
    if not People.query.get(people_id):
        return jsonify({"msg": "El personaje no existe"}), 404
    exists = FavoritePeople.query.filter_by(user_id=current_user_id, people_id=people_id).first()
    if exists:
        return jsonify({"msg": "Ya se encuentra en tus favoritos"}), 400
    new_fav = FavoritePeople(user_id=current_user_id, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Personaje agregado a favoritos"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1
    fav = FavoritePlanet.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Planeta eliminado de favoritos"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user_id = 1
    fav = FavoritePeople.query.filter_by(user_id=current_user_id, people_id=people_id).first()
    if not fav:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Personaje eliminado de favoritos"}), 200

@app.route('/init-data', methods=['GET'])
def init_data():
    try:
        user = User.query.get(1)
        if not user:
            user = User(id=1, username="test_user", email="test@starwars.com")
            db.session.add(user)
        planet = Planet.query.get(1)
        if not planet:
            planet = Planet(id=1, name="Tatooine", climate="arid", terrain="desert")
            db.session.add(planet)
        person = People.query.get(1)
        if not person:
            person = People(id=1, name="Luke Skywalker", height="172", mass="77")
            db.session.add(person)
        db.session.commit()
        return jsonify({"msg": "¡Datos de prueba creados con éxito!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
