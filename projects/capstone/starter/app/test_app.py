import unittest, json
from flask_sqlalchemy import SQLAlchemy
from app.py import create_app
from models import setup_db, Actor, Movie


class AgencyTestCase(unittest.TestCase):
    """This class represents the Casting Agency test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "agency_test"
        self.database_path = "postgresql://{}/{}".format('postgres:1234@192.168.0.108:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_movie = {
            'title': 'movie test',
            'release_date': '01-01-1999',
        }

        self.new_actor = {
            'name': 'actor test',
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
            'date': '01-01-2020',
        }

        self.update_actor_age = {
            'age': '35',
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

    # Test GET movies
    def test_get_movies(self):
        res = self.client().get('/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertTrue(len(data['movies']))

    # Test GET actors
    def test_get_actors(self):
        res = self.client().get('/actors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(len(data['actors']))

    # Test POST new movie
    def test_create_new_movie(self):
        res = self.client().post('/movies', json=self.new_movie)
        data = json.loads(res.data)
        new_movie = Movie.query.filter(Movie.id == data['movie']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie_id'])
        self.assertTrue(new_movie)

    # Test POST new actor
    def test_create_new_actor(self):
        res = self.client().post('/actors', json=self.new_actors)
        data = json.loads(res.data)
        new_actor = Actor.query.filter(Actor.id == data['actor']).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor_id'])
        self.assertTrue(new_actor)

    # Test PATCH movie
    def test_update_movie(self):
        movie_update = Movie.query.filter(Movie.title=='test movie').one_or_none()
        res = self.client().patch('/movies/'+ str(movie_update.id), json=self.update_movie_date)
        data = json.loads(res.data)

        # check if movie was updated
        movie = Movie.query.filter(Movie.id == movie_update.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie_id'], movie_update.id)
        self.assertEqual(movie.release_date, movie_update.release_date)

    # Test PATCH actor
    def test_update_actor(self):
        actor_update = Actor.query.filter(Actor.name=='test actor').one_or_none()
        res = self.client().patch('/actors/'+ str(actor_update.id), json=self.update_actor_age)
        data = json.loads(res.data)
        # check if actor was updated
        actor = Actor.query.filter(Actor.id == actor_update.id).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], actor_update.id)
        self.assertEqual(actor.age, actor_update.age)


    # Test DELETE movie
    def test_delete_movie(self):
        movie_delete = Movie.query.filter(Movie.title=='test movie').one_or_none()
        res = self.client().delete('/movies/'+ str(movie_delete.id))
        data = json.loads(res.data)
        movie = Movie.query.filter(Movie.id == movie_delete.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie_id'], movie_delete.id)
        self.assertEqual(movie, None)

    # Test DELETE actor
    def test_delete_actor(self):
        actor_delete = Actor.query.filter(Actor.name=='test actor').one_or_none()
        res = self.client().delete('/actors/'+ str(actor_delete.id))
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == actor_delete.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], actor_delete.id)
        self.assertEqual(actor, None)


    # Test Errors test

    # Error create actor missing gender 
    def test_400_for_failed_created_actor(self):
        res = self.client().post('/actors', json=self.new_actor_missing_attribute)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    # Error create movie missing release date 
    def test_400_for_failed_created_movie(self):
        res = self.client().post('/movies', json=self.new_movie_missing_attribute)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')
    
    # Error delete movie not found
    def test_404_if_movie_does_not_exist(self):
        res = self.client().delete('/movie/999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # Error delete actor not found
    def test_404_if_actor_does_not_exist(self):
        res = self.client().delete('/actor/999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # Error update actor without  parameters
    def test_422_if_actor_missing_parameters(self):
        res = self.client().patch('/actor')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')
    
    # Error update movie without  parameters
    def test_422_if_movie_missing_parameters(self):
        res = self.client().patch('/movie')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    # Tests RBAC
    def test_create_new_actor_casting_assistant(self):
        res = self.client().post('/actors',
            headers={
            "Authorization": "Bearer {}".format(
                self.casting_assistant)
            }, json=self.new_actor)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], {
            'code': 'unauthorized', 'description':
            'Permission not found.'})

    def test_create_new_movies_executive_producer(self):
        res = self.client().post('/movies',
            headers={
            "Authorization": "Bearer {}".format(
                self.executive_producer)
            }, json=self.movies)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_new_movies_casting_assistant(self):
        res = self.client().post('/movies',
            headers={

            "Authorization": "Bearer {}".format(
                self.casting_assistant)
            }, json=self.movies)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['message'], {
            'code': 'unauthorized', 'description':
            'Permission not found.'})

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()