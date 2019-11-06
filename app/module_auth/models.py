from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    spec = db.Column(db.String(64), index=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} {} {} {} {}>'.format(self.id, self.spec, self.username, self.email, self.password_hash)


class Survey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)

    unique_id = db.Column(db.String(512), index=True, unique=True)
    date = db.Column(db.String(64), index=True)
    rid = db.Column(db.String(64), index=True)
    location = db.Column(db.String(64), index=True)
    type = db.Column(db.String(64), index=True)
    survey = db.Column(db.String(64), index=True)
    pdf = db.Column(db.LargeBinary)

    def __repr__(self):
        return '<Survey {} {} {} {} {} {}>'.format(self.id, self.unique_id, self.type, self.date, self.rid, self.loc, self.pdf)
