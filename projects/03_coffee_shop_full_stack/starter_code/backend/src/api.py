import os
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
         where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def drinks():
    try:
        drinks = [drink.short() for drink in Drink.query.all()]
        return jsonify(
            {
                'success': True,
                'drinks': drinks,
            })
    except KeyError:
        print(os.sys.exc_info())
        abort(422)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(jwt):
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify(
            {
                'success': True,
                'drinks': drinks,
            })
    except KeyError:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def drinks_create(jwt):
    # if body exists
    try:
        body = request.get_json()
        drink_title = body.get('title', None)
        drink_recipe = body.get('recipe', None)
    except KeyError:
        abort(422)

    # if missing some required data
    drink_parameters = [drink_title, drink_recipe]
    if any(parameter is None for parameter in drink_parameters):
        abort(400)

    try:
        # create new drink
        new_drink = Drink(title=drink_title, recipe=json.dumps(drink_recipe))
        new_drink.insert()

        return jsonify(
            {
                'success': True,
                'drinks': new_drink.long(),
            })

    except KeyError:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where
    drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def drinks_patch(jwt, drink_id):
    # if body exists
    try:
        body = request.get_json()
        drink_title = body.get('title', None)
        drink_recipe = body.get('recipe', None)
    except KeyError:
        abort(422)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(400)

    try:
        if drink_title is not None:
            drink.title = drink_title
        if drink_recipe is not None:
            drink.recipe = json.dumps(drink_recipe)
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()],
        })

    except KeyError:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def drinks_delete(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(400)

    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id,
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


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def authentification_failed(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": AuthError.error
    }), 401
