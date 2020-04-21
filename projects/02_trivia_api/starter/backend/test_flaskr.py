import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('postgres:1234@192.168.0.108:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'test question',
            'answer': 'test answer',
            'category': 1,
            'difficulty': 1
        }

        self.new_question_missing_attribute = {
            'answer': 'test answer',
            'category': 1,
            'difficulty': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))


    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        questions_category_1 = [quest.format() for quest in Question.query.filter(Question.category==1).all()]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 1)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['questions'], questions_category_1)

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        new_question = Question.query.filter(Question.id == data['created']).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(new_question)

    def test_delete_question(self):
        question_delete = Question.query.filter(Question.question=='test question').one_or_none()

        res = self.client().delete('/questions/'+ str(question_delete.id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == question_delete.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], question_delete.id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)
    
    def test_questions_search(self):
        searchTerm = 'title'
        res = self.client().post('/questions/search', json={'searchTerm':searchTerm})
        data = json.loads(res.data)

        result_search = [quest.format() for quest in Question.query.filter(Question.question.\
                                        ilike('%{}%'.format(searchTerm))).all()]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['questions'], result_search)
        self.assertTrue(len(data['questions']))

    def test_play_quizz(self):
        category = Category.query.first()
        quiz_category = {'id':category.id, 'type':category.type}
        previous_questions = []
        res = self.client().post('/quizzes', json={'previous_questions':previous_questions,\
         'quiz_category':quiz_category})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # Test Errors
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_404_if_category_does_not_exist(self):
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_422_if_not_body_for_search(self):
        res = self.client().post('/questions/search')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_422_if_category_play_quizz(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_422_for_failed_created_question(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    
    def test_400_for_failed_created_question(self):
        res = self.client().post('/questions', json=self.new_question_missing_attribute)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()