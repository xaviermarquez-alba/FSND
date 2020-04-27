import unittest, json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Actor, Movie
import os
from datetime import datetime

class AgencyTestCase(unittest.TestCase):
    """This class represents the Casting Agency test case"""

    # Create test data for actor and movie
    actor_test_update = Actor(name='actor update test', age=30, gender='male')
    actor_test_update.insert()
    actor_test_delete = Actor(name='actor delete test', age=30, gender='male')
    actor_test_delete.insert()

    movie_test_update = Movie(title='movie update test', release_date=datetime.strptime('1999-01-01','%Y-%m-%d'))
    movie_test_update.insert()
    movie_test_delete = Movie(title='movie delete test', release_date=datetime.strptime('1999-01-01','%Y-%m-%d'))
    movie_test_delete.insert()

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ['DATABASE_URL']
        setup_db(self.app, self.database_path)

        self.jwt_all_permissions = os.environ['JWT_TOKEN']
        self.jwt_casting_assistant = os.environ['JWT_CASTING_ASSIST']
        self.jwt_casting_director = os.environ['JWT_CASTING_DIRECTOR']
        self.jwt_executive_producer = os.environ['JWT_EXECUTIVE_PRODUCER']

        self.new_movie = {
            'title': 'test movie',
            'release_date': '1999-01-01',
        }

        self.new_actor = {
            'name': 'test actor',
            'age': '25',
            'gender': 'male',
        }

        self.new_movie_missing_attribute = {
            'title': 'test movie',
        }

        self.new_actor_missing_attribute = {
            'name': 'test actor',
            'age': '25',
        }

        self.update_movie_date = {
            'release_date': '1999-01-01',
        }

        self.update_actor_age = {
            'age': 35,
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Remove test data for actor and movie after all tests
        movie_update_test = Movie.query.filter(Movie.title == 'movie update test').one_or_none()
        if movie_update_test:
            movie_update_test.delete()
        
        movie_delete_test = Movie.query.filter(Movie.title == 'movie update test').one_or_none()
        if movie_delete_test:
            movie_delete_test.delete()

        actor_test_update = Actor.query.filter(Actor.name == 'actor update test').one_or_none()
        if actor_test_update: 
            actor_test_update.delete()
        
        actor_test_delete = Actor.query.filter(Actor.name == 'actor update test').one_or_none()
        if actor_test_delete:
            actor_test_delete.delete()

    # Test GET movies
    def test_get_movies(self):
        res = self.client().get('/movies', headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertTrue(len(data['movies']))

    # Test GET actors
    def test_get_actors(self):
        res = self.client().get('/actors', headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(len(data['actors']))

    # Test POST new movie
    def test_create_new_movie(self):
        res = self.client().post('/movies', json=self.new_movie, headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        new_movie = Movie.query.filter(Movie.id == data['movie_id']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie_id'])
        self.assertTrue(new_movie)

    # Test POST new actor
    def test_create_new_actor(self):
        res = self.client().post('/actors', json=self.new_actor, headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        new_actor = Actor.query.filter(Actor.id == data['actor_id']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor_id'])
        self.assertTrue(new_actor)

    # Test PATCH movie
    def test_update_movie(self):
        movie_update = Movie.query.filter(Movie.title=='movie update test').one_or_none()
        res = self.client().patch('/movies/'+ str(movie_update.id), json=self.update_movie_date, headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)

        # check if movie was updated
        movie = Movie.query.filter(Movie.id == movie_update.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie_id'], movie_update.id)
        self.assertEqual(movie.release_date, movie_update.release_date)

    # Error update movie without  parameters
    def test_422_if_movie_missing_parameters(self):
        movie_update = Movie.query.filter(Movie.title=='movie update test').one_or_none()
        res = self.client().patch('/movies/'+ str(movie_update.id), headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    # Test PATCH actor
    def test_update_actor(self):
        actor_update = Actor.query.filter(Actor.name=='actor update test').one_or_none()
        res = self.client().patch('/actors/'+ str(actor_update.id), json=self.update_actor_age, headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        # check if actor was updated
        actor = Actor.query.filter(Actor.id == actor_update.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], actor_update.id)
        self.assertEqual(actor.age, self.update_actor_age['age'])

    # Error update actor without  parameters
    def test_422_if_actor_missing_parameters(self):
        actor_update = Actor.query.filter(Actor.name=='actor update test').one_or_none()
        res = self.client().patch('/actors/' + str(actor_update.id), headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    # Error create actor missing gender 
    def test_400_for_failed_created_actor(self):
        res = self.client().post('/actors', json=self.new_actor_missing_attribute, headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    # Error create movie missing release date 
    def test_400_for_failed_created_movie(self):
        res = self.client().post('/movies', json=self.new_movie_missing_attribute, headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')
    
    # Error delete movie not found
    def test_404_if_movie_does_not_exist(self):
        res = self.client().delete('/movies/999', headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # Error delete actor not found
    def test_404_if_actor_does_not_exist(self):
        res = self.client().delete('/actors/999', headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # Test DELETE movie
    def test_delete_movie(self):
        movie_delete = Movie.query.filter(Movie.title=='movie delete test').one_or_none()
        res = self.client().delete('/movies/'+ str(movie_delete.id), headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        movie = Movie.query.filter(Movie.id == movie_delete.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie_id'], movie_delete.id)
        self.assertEqual(movie, None)

    # Test DELETE actor
    def test_delete_actor(self):
        actor_delete = Actor.query.filter(Actor.name=='actor delete test').one_or_none()
        res = self.client().delete('/actors/'+ str(actor_delete.id), headers={"Authorization": "Bearer {}".format(self.jwt_all_permissions)})
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == actor_delete.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], actor_delete.id)
        self.assertEqual(actor, None)

    # Tests RBAC
    # Test Casting Assitant
    def test_create_new_actor_casting_assistant(self):
        res = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(self.jwt_casting_assistant)}, json=self.new_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], {'code': 'unauthorized', 'description':'Permission not found.'})

    def test_get_movies_casting_assistant(self):
        res = self.client().get('/movies', headers={"Authorization": "Bearer {}".format(self.jwt_casting_assistant)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertTrue(len(data['movies']))

    # Tests Casting Director
    def test_create_new_actor_casting_director(self):
        res = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(self.jwt_casting_director)}, json=self.new_actor)
        data = json.loads(res.data)
        new_actor = Actor.query.filter(Actor.id == data['actor_id']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor_id'])
        self.assertTrue(new_actor)

    def test_create_new_movie_casting_director(self):
        res = self.client().post('/movies', json=self.new_movie, headers={"Authorization": "Bearer {}".format(self.jwt_casting_director)})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], {'code': 'unauthorized', 'description':'Permission not found.'})

    # Test Executive Producer
    def test_create_new_actor_executive_producer(self):
        res = self.client().post('/actors', headers={"Authorization": "Bearer {}".format(self.jwt_executive_producer)}, json=self.new_actor)
        data = json.loads(res.data)
        new_actor = Actor.query.filter(Actor.id == data['actor_id']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor_id'])
        self.assertTrue(new_actor)

    def test_create_new_movie_executive_producer(self):
        res = self.client().post('/movies', json=self.new_movie, headers={"Authorization": "Bearer {}".format(self.jwt_executive_producer)})
        data = json.loads(res.data)
        new_movie = Movie.query.filter(Movie.id == data['movie_id']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie_id'])
        self.assertTrue(new_movie)




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()