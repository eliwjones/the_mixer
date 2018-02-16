import json
import os
import sqlite3
from flask import g, Flask, jsonify, request

app = Flask(__name__)

DATABASE = 'mixer.db'
SCHEMA_FILENAME = 'mixer_schema.sql'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_is_new = not os.path.exists(DATABASE)
        db = g._database = sqlite3.connect(DATABASE)
        if db_is_new:
            print 'Creating mixer_schema'
            with open(SCHEMA_FILENAME, 'rt') as f:
                schema = f.read()
            db.executescript(schema)
    return db


@app.route('/')
def hello():
    return 'This is the Mixer.'


@app.route('/api/receive', methods=['POST'])
def receive():
    if not request.json or not 'addresses' in request.json:
        abort(400)

    addresses = request.json['addresses']
    if not isinstance(addresses, list):
        abort(400)

    cursor = get_db().cursor()
    cursor.execute("""
      INSERT INTO addresses
        (destination_addresses)
      VALUES
        ('%s')
    """ % (json.dumps(addresses)))
    get_db().commit()

    deposit_address = "mixer-%d" % (cursor.lastrowid)

    cursor.close()

    return jsonify({"deposit_address": deposit_address})


if __name__ == '__main__':
    app.run(debug=True)
