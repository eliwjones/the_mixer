import json
import os
import sqlite3
from conf import DATABASE, SCHEMA_FILENAME
from conf import deposit_address_from_index
from flask import abort, g, Flask, jsonify, request

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_is_new = not os.path.exists(DATABASE)
        db = g._database = sqlite3.connect(DATABASE)
        if db_is_new:
            print('Creating mixer_schema')
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
        abort(400, "Please pass json content like:  {'addresses': ['addr1']}")

    addresses = request.json['addresses']
    if not isinstance(addresses, list):
        abort(400, '"addresses" must be an array.')
    if not addresses:
        abort(400, '"addresses" cannot be empty.')

    con = get_db()

    cursor = con.cursor()
    cursor.execute("""
      INSERT INTO deposit_addresses DEFAULT VALUES
    """)

    con.commit()

    deposit_address_id = cursor.lastrowid
    deposit_address = deposit_address_from_index(deposit_address_id)
    """
      Attempt to insert the addresses here.
    """
    sql = ""
    for destination_address in addresses:
        sql += """
          INSERT INTO destination_addresses
            (deposit_address_id, destination_address)
          VALUES
            (%d, '%s');
        """ % (deposit_address_id, destination_address)

    # sqlite3 hackery to force rollback of all inserts.
    sql = "BEGIN; %s COMMIT;" % (sql)
    try:
        con.executescript(sql)
    except Exception as e:
        con.executescript("ROLLBACK;")
        message = "At least one of your destination addresses is already in use."
        message += " Exception: %s" % (e)
        abort(400, message)
    """
     Technically, one wants try, catch, finally and close.

     But here, I'm not going to worry about that.
    """
    cursor.close()

    return jsonify({"deposit_address": deposit_address})


if __name__ == '__main__':
    app.run(debug=True)
