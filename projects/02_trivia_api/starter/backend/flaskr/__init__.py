from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Autorization')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def categories_retrieve():
        response = {}
        categories = Category.query.order_by(Category.id).all()

        for cat in categories:
            response[cat.id] = cat.type

        return jsonify(
            {
                'success': True,
                'categories': response,
                'total_categories': len(response)
            })

    @app.route('/questions')
    def questions_retrieve():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = {}
        for cat in Category.query.all():
            categories[cat.id] = cat.type

        return jsonify(
            {
                'success': True,
                'questions': current_questions,
                'categories': categories,
                'total_questions': len(selection)
            })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def question_delete(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question is None:
            abort(422)

        try:
            question.delete()

            # current questions
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'question': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except KeyError:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def question_create():
        try:
            body = request.get_json()
            question_text = body.get('question', None)
            answer = body.get('answer', None)
            category = body.get('category', None)
            difficulty = body.get('difficulty', None)
        except KeyError:
            abort(422)

        # if missing some required data
        elems = [question_text, answer, category, difficulty]
        if any(elem is None for elem in elems):
            abort(400)

        try:
            # create new question
            question = Question(question=question_text, answer=answer,
                                category=category, difficulty=difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })

        except KeyError:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def question_search():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', None)

            if search_term is None:
                abort(422)

            # query if search term is included on question text
            selection = Question.query.filter(
                Question.question.ilike('%{}%'.format(search_term))).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection),
                    'category': None
                })

        except KeyError:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def questions_by_catergory(category_id):
        # category exists
        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        if category is None:
            abort(404)
        # questions by category name
        selection = Question.query.order_by(
            Question.id).filter_by(category=category_id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify(
            {
                'success': True,
                'current_category': category_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        try:

            previous_questions = body.get('previous_questions', None)
            category = body.get('quiz_category', None)

            # check if category is 0 = all categories
            if category["id"] == 0:
                questions = Question.query.filter(
                    ~Question.id.in_(previous_questions))
            else:
                questions = Question.query.filter(
                    Question.category == category["id"]).filter(
                    ~Question.id.in_(previous_questions))

            question = questions.first()
            if question:
                question = question.format()
            else:
                question = None

            return jsonify(
                {
                    'success': True,
                    'question': question,
                })

        except KeyError:
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(
            {
                "success": False,
                "error": 400,
                "message": "Bad request"
            }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(
            {
                "success": False,
                "error": 404,
                "message": "Resource not found"
            }), 404

    @app.errorhandler(405)
    def not_found(error):
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

    return app
