# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

## Endpoints

```
GET '/categories'
GET '/questions'
GET '/categories/<int:category_id>/questions'
POST '/questions'
POST '/questions/search'
POST '/quizzes'
DELETE '/questions/<int:question_id>'
```

#### GET '/categories'

- Fetches a dictionary for all available categories
- Request Arguments: None
- Returns:
```
{
 'success': True,                   # request status 
 'categories':                      # Dict with categories { 'id': 'name' }
 'total_categories':                # Int: total of categories
}
```


#### GET '/questions'

- Fetches a list of questions, number of total questions, current category, categories. The list of questions are in groups of 10, the  group number is defined by a parameter "page"
- Request Arguments: GET parameter 'page' to indicate the group of questions

- Returns:
```
{
  'success': True,
  'questions':                   # List of questions dicts
  'categories':                  # Dict with categories { 'id': 'name' }
  'total_questions':             # Int: total of questions
}
```

#### GET '/categories/category_id/questions'

- Fetches a dictionary of questions questions based on category, the questions are in groups of 10, the  group number is defined by a parameter "page" 
- Request Arguments: GET parameter 'page' to indicate group number

- Returns:
```
{
  'success': True,
  'current_category':           # Selected category ID
  'questions':                  # List of questions dicts
  'total_questions':            # Int: total of questions
}
```

#### POST '/questions'

- Create a new question, require the question and answer text, category, and difficulty score
- Request Arguments: 
    + question: (string)
    + answer: (string)
    + category: category id (int)
    + difficulty: (int) 

- Returns:
```
{
    'success': True,
    'created':                          # ID of the new created question
    'questions':                        # list of questions
    'total_questions':                  # total questions
}
```

#### POST '/questions/search'

- Search questions based on a search term, if the search term is included in the question text
- Request Arguments: 
    + searchTerm: (string)

- Returns:
```
{
    'success': True,
    'questions':                        # list of questions
    'total_questions':                  # total questions
}
```

#### POST '/quizzes'

- This endpoint take category and previous question parameters 
  and return a random questions within the given category excluding previous questions

- Request Arguments:
    + previous_questions: list of previous questions IDs
    + quiz_category: category ID to play the quiz     

- Returns:
```
{
    'success': True,
    'question':                         # question           
} 
```

#### DELETE '/questions/question_id'

- Delete a question using a question ID.
- Request Arguments:
    + question_id: (int)

- Returns:
```
{
    'success': True,
    'question':                 # deleted question ID
    'questions':                # list of current questions
    'total_questions':          # int total of questions remaining
} 
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```