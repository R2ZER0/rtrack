import sys
from datetime import datetime
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from flask.ext.cors import CORS
from flask.ext.sqlalchemy import SQLAlchemy

# config
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/rtrack.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
SECRET_KEY = 'a_secret_key'

# our app
app = Flask(__name__)
app.config.from_object(__name__)
cors = CORS(app)
db = SQLAlchemy(app)

class Record(db.Model):
    __tablename__ = 'record'
    """A tracking record with the location (and maybe now playing song)"""
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.String(64), nullable=False)
    longitude = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_handle = db.Column(db.String(32), db.ForeignKey('user.handle'))
    now_playing = db.Column(db.String, nullable=True)

    def to_output_values(self):
        return {
            latitude: self.latitude,
            longitude: self.longitude,
            # WARNING: only works on Linux! (or at least, not Windows)
            timestamp: int(self.timestamp.strftime("%s"))*1000,
            now_playing: self.now_playing
        }

    def init(self, latitude, longitude, timestamp, user, now_playing=None):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.user = user
        self.now_playing = now_playing

    def __repr__(self):
        return '<Record {} {} {}>'.format(self.latitude, self.longitude, self.timestamp)

class User(db.Model):
    __tablename__ = 'user'
    """A user handle for auth uploading records"""
    handle = db.Column(db.String(32), unique=True, nullable=False, primary_key=True)
    passkey = db.Column(db.String, nullable=False)
    records = db.relationship('Record', backref='user', lazy='dynamic')

    def __init__(self, handle, passkey):
        self.handle = handle
        self.passkey = passkey

    @classmethod
    def new(cls, handle, passkey):
        if User.query.filter_by(handle=handle).count() > 0:
            raise Exception("User already exists")
        else:
            user = User(handle, passkey)
            db.session.add(user)
            db.session.commit()
            return user

    @classmethod
    def by_handle(cls, handle):
        return cls.query.filter_by(handle=handle).first()

    @property
    def latest_record(self):
        return self.records.order_by('timestamp desc').limit(1).first()

    def __repr__(self):
        return '<User {}>'.format(self.handle)


@app.route('/<handle>')
@app.route('/<handle>/latest')
def show_location(handle):
    try:
        latest = User.by_handle(handle).latest_record
        return jsonify(
            success=True,
            latitude=latest.latitude,
            longitude=latest.longitude,
            timestamp=latest.timestamp,
            now_playing=latest.now_playing
        )
    except:
        if DEBUG:
            raise
        else:
            return jsonify(success=False, error='No such user')

@app.route('/<handle>/history')
@app.route('/<handle>/history/<int:tsfrom>')
@app.route('/<handle>/history/<int:tsfrom>/<int:tsto>')
def history(handle, tsfrom=None, tsto=None):
    # TODO

    # All history

    # From specified

    # Both from and to specified

    # send { history: [ records... ] }
    #return jsonify(history=records)
    return jsonify(success=False, error="todo")

@app.route('/<handle>/update/<key>', methods=['POST'])
def update_location(handle, key):
    try:
        user = User.by_handle(handle)
        if key == user.passkey:
            record = Record(
                latitude = request.form['latitude'],
                longitude = request.form['longitude'],
                timestamp = datetime.utcfromtimestamp(float(request.form['timestamp'])/1000.0),
                user_handle = user.handle,
                now_playing = request.form.get('now_playing', None)
            )
            db.session.add(record)
            db.session.commit()
            return jsonify(success=True)

        else:
            response = jsonify(success=False, error="Incorrect user or key")
            response.status_code = 401
            return response

    except:
        if DEBUG:
            raise
        else:
            response = jsonify(success=False, error="Incorrect user or bad request (or something just broke)")
            response.status_code = 400
            return response

@app.route('/newuser', methods=['POST'])
def newuser():
    try:
        handle = request.form['user']
        passkey = request.form['passkey']
        User.new(handle, passkey)
        return jsonify(success=True)
    except:
        response = jsonify(success=False, error="User already exists or bad request (or something just broke)")
        response.status_code = 400
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
