from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import *
from auth import AuthError, requires_auth
from datetime import datetime

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
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
    def movies_retrieve(jwt):
        q_movie = Movie.query.all()
        movies = [movie.format() for movie in q_movie]

        return jsonify(
            {
                'success': True,
                'movies': movies,
            })

    # GET all actors
    @app.route('/actors')
    @requires_auth('get:actors')
    def actors_retrieve(jwt):
        q_actors = Actor.query.all()
        actors = [actor.format() for actor in q_actors]
        return jsonify(
            {
                'success': True,
                'actors': actors,
            })

    # Create a new movie
    @app.route('/movies', methods=['POST'])
    @requires_auth('post:movies')
    def movies_create(jwt):
        # if body exists
        try:
            body = request.get_json()
            movie_title = body.get('title', None)
            movie_release_date = body.get('release_date', None)
        except KeyError:
            abort(422)

        # if missing some required data
        if any(parameter is None for parameter in [movie_title, movie_release_date]):
            abort(400)

        try:
            # create new movie
            movie_release_date = datetime.strptime(movie_release_date, "%Y-%m-%d")
            new_movie = Movie(title=movie_title, release_date=movie_release_date)
            new_movie.insert()
            movie_id = new_movie.id

            return jsonify(
                {
                    'success': True,
                    'movie_id': movie_id,
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
            abort(400)

        try:
            # create new actor
            new_actor = Actor(name=actor_name, age=actor_age,
                              gender=actor_gender)
            new_actor.insert()
            actor_id = new_actor.id

            return jsonify(
                {
                    'success': True,
                    'actor_id': actor_id,
                })

        except KeyError:
            abort(422)

    # Create a movie_actor relation
    @app.route('/movies/actors', methods=['POST'])
    @requires_auth('post:movies_actors')
    def movie_actor_create(jwt):

        # if body exists
        try:
            body = request.get_json()
            actor_id = body.get('actor_id', None)
            movie_id = body.get('movie_id', None)
        except KeyError:
            abort(422)

        # check if missing some required data
        if any(parameter is None for parameter in [actor_id, movie_id]):
            abort(400)

        # check if movie exists
        movie = Movie.query.get(movie_id)
        if not movie:
            abort(404)
        # check if actor exist
        actor = Actor.query.get(actor_id)
        if not actor:
            abort(404)

        try:
            # add actor to movie
            movie.actor_movie = [actor]
            movie.update()

            return jsonify(
                {
                    'success': True,
                    'actor_id': actor_id,
                    'movie_id': movie_id
                })

        except KeyError:
            abort(422)

    # Update movie by ID
    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('patch:movies')
    def movie_patch(jwt, movie_id):
        # if body exists
        body = request.get_json()
        if body:
            movie_title = body.get('title', None)
            movie_release_date = body.get('release_date', None)
        else:
            abort(422)

        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if movie is None:
            abort(404)

        try:
            # check parameter to update
            if movie_title is not None:
                movie.title = movie_title
            if movie_release_date is not None:
                movie_release_date = datetime.strptime(movie_release_date, "%Y-%m-%d")
                movie.release_date = movie_release_date

            movie.update()
            return jsonify({
                'success': True,
                'movie_id': movie_id,
            })

        except KeyError:
            abort(422)


    # Update actor by ID
    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('patch:actors')
    def actor_patch(jwt, actor_id):
        # if body exists
        body = request.get_json()
        if body:
            actor_name = body.get('name', None)
            actor_age = body.get('age', None)
            actor_gender = body.get('gender', None)
        else:
            abort(422)

        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)

        try:
            # check parameter to update
            if actor_name is not None:
                actor.name = actor_name
            if actor_age is not None:
                actor.age = actor_age
            if actor_gender is not None:
                actor.gender = actor_gender

            actor.update()

            return jsonify({
                'success': True,
                'actor_id': actor_id,
            })

        except KeyError:
            abort(422)

    # Delete movie by ID
    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movies')
    def movies_delete(jwt, movie_id):
        movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        if movie is None:
            abort(404)

        try:
            movie.delete()
            return jsonify({
                'success': True,
                'movie_id': movie_id,
            })

        except KeyError:
            abort(422)

    # Delete actor by ID
    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actors')
    def actors_delete(jwt, actor_id):
        actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        if actor is None:
            abort(404)

        try:
            actor.delete()
            return jsonify({
                'success': True,
                'actor_id': actor_id,
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
                "message": "Unauthorized"
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
                "message": "Unprocessable entity"
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
