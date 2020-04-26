import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models.py import Movies, Actor
from auth.py import AuthError, requires_auth

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__)
	CORS(app)

	@app.after_request
	def after_request(response):
		response.headers.add(
		'Access-Control-Allow-Headers', 'Content-Type, Autorization')
		response.headers.add(
		'Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
		return response

	# GET all movies
	@app.route('/movies')
	@requires_auth('get:movies')
   	def movies_retrieve():
	    movies = Movies.query.all()
	    return jsonify(
	        {
	            'success': True,
	            'categories': movies,
	        })

    # GET all actors
	@app.route('/actors')
	@requires_auth('get:actors')
   	def actors_retrieve():
	    actors = Actor.query.all()
	    return jsonify(
	        {
	            'success': True,
	            'categories': actors,
	        })

	# Create a new movie
	@app.route('/movies', methods=['POST'])
	@requires_auth('post:movies')
	def movies_create(jwt):
	    # if body exists
	    try:
	        body = request.get_json()
	        movie_title = body.get('title', None)
	        movie_date = body.get('date', None)
	    except KeyError:
	        abort(422)

	    # if missing some required data
	    movie_parameters = [movie_title, movie_date]
	    if any(parameter is None for parameter in movie_parameters):
	        abort(401)

	    try:
	        # create new movie
	        new_movie = Movies(title=movie_title, release_date=movie_date)
	        new_movie.insert()
	        movie_id = new_movie.id

	        return jsonify(
	            {
	                'success': True,
	                'movie': movie_id,
	            })

	    except KeyError:
	        abort(422)

	# Create a new actor
	@app.route('/actors', methods=['POST'])
	@requires_auth('post:actors')
	def actors_create(jwt):
	    
	    # if body exists
	    try:
	        body = request.get_json()
	        actor_name = body.get('name', None)
	        actor_age = body.get('age', None)
	        actor_gender = body.get('gender', None)
	    
	    except KeyError:
	        abort(422)

	    # check if missing some required data
	    actor_parameters = [actor_name, actor_gender, actor_age]
	    if any(parameter is None for parameter in actor_parameters):
	        abort(401)

	    try:
	        # create new actor
	        new_actor = Actor(name=actor_name, age=actor_age, actor_gender)
	        new_actor.insert()
	        actor_id = new_actor.id

	        return jsonify(
	            {
	                'success': True,
	                'actor': actor_id,
	            })

	    except KeyError:
	        abort(422)

    # Update movie by ID
	@app.route('/movies/<int:movie_id>', methods=['PATCH'])
	@requires_auth('patch:movies')
	def movie_patch(jwt, movie_id):
	    # if body exists
	    try:
	        body = request.get_json()
	        movie_title = body.get('title', None)
	        movie_date = body.get('date', None)
	    except KeyError:
	        abort(422)

	    movie = Movies.query.filter(Movies.id == movie_id).one_or_none()
	    if movie is None:
	        abort(400)

	    try:
	    	# check parameter to update
	        if movie_title is not None:
	            movie.title = movie_title
	        if movie_date is not None:
	            movie.release_date = movie_date
	        
	        movie.update()
	        return jsonify({
	            'success': True,
	            'movie': movie_id,
	        })

	    except KeyError:
	        abort(422)


    # Update actor by ID
	@app.route('/actors/<int:actor_id>', methods=['PATCH'])
	@requires_auth('patch:actors')
	def actor_patch(jwt, actor_id):
	    # if body exists
	    try:
	        body = request.get_json()
	        actor_name = body.get('name', None)
	        actor_age = body.get('age', None)
	        actor_gender = body.get('gender', None)
	    except KeyError:
	        abort(422)

	    actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
	    if actor is None:
	        abort(400)

	    try:
	    	# check parameter to update
	        if actor_title is not None:
	            actor.title = actor_title
	        if actor_age is not None:
	            actor.age = actor_age
	        if actor_gender is not None:
	            actor.gender = actor_gender

	        actor.update()

	        return jsonify({
	            'success': True,
	            'actor': actor_id,
	        })

	    except KeyError:
	        abort(422)

    # Delete movie by ID
	@app.route('/movies/<int:movie_id>', methods=['DELETE'])
	@requires_auth('delete:movies')
	def movies_delete(jwt, movie_id):
	    movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
	    if movie is None:
	        abort(400)

	    try:
	        movie.delete()
	        return jsonify({
	            'success': True,
	            'delete': movie_id,
	        })

	    except KeyError:
	        abort(422)

    # Delete actor by ID
	@app.route('/actors/<int:actor_id>', methods=['DELETE'])
	@requires_auth('delete:actors')
	def actors_delete(jwt, actor_id):
	    actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
	    if actor is None:
	        abort(400)

	    try:
	        actor.delete()
	        return jsonify({
	            'success': True,
	            'delete': actor_id,
	        })

	    except KeyError:
	        abort(422)


    # Error Handling
	@app.errorhandler(400)
	def bad_request(error):
	    return jsonify(
	        {
	            "success": False,
	            "error": 400,
	            "message": "Bad request"
	        }), 400


	@app.errorhandler(401)
	def unauthorized(error):
	    return jsonify(
	        {
	            "success": False,
	            "error": 401,
	            "message": "Unauthorized "
	        }), 401


	@app.errorhandler(403)
	def forbidden(error):
	    return jsonify(
	        {
	            "success": False,
	            "error": 403,
	            "message": "Forbidden"
	        }), 403


	@app.errorhandler(404)
	def not_found(error):
	    return jsonify(
	        {
	            "success": False,
	            "error": 404,
	            "message": "Resource not found"
	        }), 404


	@app.errorhandler(405)
	def not_allowed(error):
	    return jsonify(
	        {
	            "success": False,
	            "error": 405,
	            "message": "Method not allowed"
	        }), 405


	@app.errorhandler(422)
	def unprocessable(error):
	    return jsonify(
	        {
	            "success": False,
	            "error": 422,
	            "message": "Unprocessable"
	        }), 422


	@app.errorhandler(500)
	def server_error(error):
	    return jsonify(
	        {
	            "success": False,
	            "error": 500,
	            "message": "Internal server error"
	        }), 500

	# AuthError error handler
	@app.errorhandler(AuthError)
	def authentification_failed(AuthError):
	    return jsonify({
	        "success": False,
	        "error": AuthError.status_code,
	        "message": AuthError.error
	    }), 401


	return app



APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)