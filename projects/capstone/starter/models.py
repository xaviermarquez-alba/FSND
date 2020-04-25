import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
# TODO pass to postgresql
database_path = "sqlite:///{}".format(os.path.join(project_dir, database_filename))

db = SQLAlchemy()

'''
setup_db(app) binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
    drops the database tables and starts fresh can be used to initialize a clean database
'''
#db_drop_and_create_all()

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

# Actor by movie
actor_movie = db.Table('Actor_movie',
    db.Column('Actor', db.Integer, db.ForeignKey('Actor.id'), primary_key=True),
    db.Column('Movie', db.Integer, db.ForeignKey('Movie.id'), primary_key=True),
  )

class Movie(db.Model):
    __tablename__ = 'Movie'
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    title = Column(String(100), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)
    actor_movie = db.relationship('Actor', secondary=actor_movie, backref=db.backref('actor_movie'), lazy='dynamic')

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

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

    def __repr__(self):
        return self.name


