import json
import os
import sqlite3
from conf import DATABASE, SCHEMA_FILENAME
from conf import deposit_address_from_index
from flask import g, Flask, jsonify, request

app = Flask(__name__)


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


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def hello():
    return 'This is the Mixer.'


@app.route('/api/receive', methods=['POST'])
def receive():
    """This is a fairly simple approach to letting people set up destination_addresses
    and to get a new deposit address without providing any additional information.

    IF denial of service attacks became a problem, one could institute a dynamic
    proof-of-work requirement for POSTs to this endpoint.

    Something like:
    
        hash = SHA256("<timestamp>-<json_serialized_destination_addresses>-<some_number>)

    Verified with:

        hash.startswith("0000") and is_kosher(request.json['timestamp'])

    Or whatnot, depending on the client side rate limiting we desire.

    This could suck for the "good actors", but feels like a good approach to explore
    since good actors shouldn't need to be perpetually creating new deposit, destinations
    pairings.
    """
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

    deposit_address = deposit_address_from_index(cursor.lastrowid)
    """
     Technically, one wants try, catch, finally and close.

     But here, I'm not going to worry about that.
    """
    cursor.close()

    return jsonify({"deposit_address": deposit_address})


if __name__ == '__main__':
    app.run(debug=True)
