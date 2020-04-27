import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    # db_drop_and_create_all()

'''
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to have multiple verisons of a database
'''
# Actor by movie
actor_movie = db.Table('actor_movie',
    db.Column('Actor', db.Integer, db.ForeignKey('Actor.id'), primary_key=True),
    db.Column('Movie', db.Integer, db.ForeignKey('Movie.id'), primary_key=True),
  )

class Movie(db.Model):
    __tablename__ = 'Movie'
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(100), nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    actor_movie = db.relationship('Actor', secondary=actor_movie, backref=db.backref('actor_movie'), lazy='dynamic')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):   
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.strftime('%Y-%m-%d')
        }

    def __repr__(self):
        return self.title

class Actor(db.Model):
    __tablename__ = 'Actor'
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    name = Column(String(120), nullable=False)
    age = Column(db.Integer, nullable=False)
    gender = db.Column(db.String(120), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }

    def __repr__(self):
        return self.name


