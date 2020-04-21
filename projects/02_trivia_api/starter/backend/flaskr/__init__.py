import os
from os import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Autorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
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

    return jsonify({
      'success': True,
      'categories': response,
      'total_categories': len(response)
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def questions_retrieve():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    if len(current_questions) == 0:
      abort(404)

    categories = {}
    for cat in Category.query.all():
      categories[cat.id] = cat.type

    return jsonify({
      'success': True,
      'questions': current_questions,
      'categories': categories,
      'total_questions': len(selection)
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def question_delete(question_id):
    question = Question.query.filter(Question.id==question_id).one_or_none()
    
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
    
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def question_create():
    try:
      body = request.get_json()
      question_text = body.get('question', None)
      answer = body.get('answer', None)
      category = body.get('category', None)
      difficulty = body.get('difficulty', None)
    except:
      abort(422)
    
    # if missing some required data
    if any(elem is None for elem in [question_text, answer, category, difficulty]):
      abort(400)

    try:
      # create new question
      question = Question(question=question_text, answer=answer, 
                            category=category, difficulty=difficulty)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(selection)
      })

    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def question_search():
    try:

      body = request.get_json()
      search_term = body.get('searchTerm', None)

      if search_term is None:
        abort(422)

      # query if search term is included on question text
      selection = Question.query.filter(Question.question.\
                                        ilike('%{}%'.format(search_term))).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'category': None
      })

    except:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def questions_by_catergory(category_id):
    # category exists

    category = Category.query.filter(Category.id==category_id).one_or_none()
    if category is None:
      abort(404)
    # questions by category name
    selection = Question.query.order_by(Question.id).\
                                          filter_by(category=category_id).all()
    current_questions = paginate_questions(request, selection)
    
    return jsonify({
      'success': True,
      'current_category': category_id,
      'questions': current_questions,
      'total_questions': len(selection)
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    body = request.get_json()
    try:

      previous_questions = body.get('previous_questions', None)
      category = body.get('quiz_category', None)

      # check if category is 0 = all categories
      if category["id"] == 0:
        questions = Question.query.filter(~Question.id.in_(previous_questions))
      else:
        questions = Question.query.filter(Question.category==category["id"]).\
                                    filter(~Question.id.in_(previous_questions))
      
      question = questions.first()
      if question:
        question = question.format()
      else:
        question = None

      return jsonify({
        'success': True,
        'question': question,
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Resource not found"
        }), 404

  @app.errorhandler(405)
  def not_found(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method not allowed"
        }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
      }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "Internal server error"
      }), 500
  
  return app

    