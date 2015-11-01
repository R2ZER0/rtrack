import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from flask.ext.cors import CORS

# config
DATABASE = 'rtrack.db'
DEBUG = True
SECRET_KEY = 'a_secret_key'

# our app
app = Flask(__name__)
app.config.from_object(__name__)

cors = CORS(app)

def connect_db():
  return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
  g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

@app.route('/<user>')
def show_location(user):
  cur = g.db.execute("""
    select latitude, longitude, timestamp from records
    where user = ?
    order by timestamp desc
    limit 1""", [user])
  record = [dict(latitude=row[0], longitude=row[1], timestamp=row[2]) for row in cur.fetchall()][0]
  return jsonify(record)

@app.route('/<user>/history')
@app.route('/<user>/history/<int:tsfrom>')
@app.route('/<user>/history/<int:tsfrom>/<int:tsto>')
def history(user, tsfrom=None, tsto=None):
    cur = None
    # All history
    if not tsfrom and not tsto:
        cur = g.db.execute("""
            select latitude, longitude, timestamp from records
            where user = ?
            order by timestamp desc
            """, [user])

    # From specified
    elif not tsto and tsfrom:
        cur = g.db.execute("""
            select latitude, longitude, timestamp from records
            where user = ?
            and timestamp >= ?
            order by timestamp desc
            """, [user, tsfrom])

    # Both from and to specified
    else:
        cur = g.db.execute("""
            select latitude, longitude, timestamp from records
            where user = ?
            and timestamp >= ?
            and timestamp <= ?
            order by timestamp desc
            """, [user, tsfrom, tsto])

    records = [ dict(latitude=row[0], longitude=row[1], timestamp=row[2]) for row in cur.fetchall() ]
    return jsonify(history=records)

@app.route('/<user>/update/<key>', methods=['POST'])
def update_location(key):
    if key == SECRET_KEY:
        g.db.execute('insert into records (latitude, longitude, timestamp, user) values (?, ?, ?, ?)', [
                     request.form['latitude'],
                     request.form['longitude'],
                     request.form['timestamp'],
                     request.form['user']
        ])
        g.db.commit()
        return jsonify(success=True)

    else:
        response = jsonify(success=False, error="Incorrect Key")
        response.status_code = 401
        return response

if __name__ == '__main__':
  app.run(host='0.0.0.0', threaded=True)
