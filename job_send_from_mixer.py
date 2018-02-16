import json
import random
import requests
import sqlite3
from conf import DATABASE, DISPERSAL_UNIT, JOBCOIN_API, JOB_SEND_FROM_LOG, MIXER_ADDRESS
from conf import index_from_deposit_address, deposit_address_from_index
from datetime import datetime
from decimal import Decimal

started = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
with open(JOB_SEND_FROM_LOG, 'a') as f:
    log_line = "[%s] Job Send From Mixer Started.\n" % (started)
    print log_line
    f.write(log_line)

con = sqlite3.connect(DATABASE)

total_dispersed = 0
deposit_to_destinations = {}
destination_to_deposits = {}

with con:
    for row in con.execute("SELECT deposit_address_id, destination_addresses FROM addresses"):
        deposit_address = deposit_address_from_index(row[0])
        destination_addresses = json.loads(row[1])

        deposit_to_destinations[deposit_address] = destination_addresses
        """
          Technically, we have no guarantee that a destination_address hasn't been
          submitted for more than one deposit_address.

          BUT, I'm just going to assume I've used a more aggressive db schema that ensures
          each new list of addresses posted to 'api/recieve' have not been used before.
        """
        for destination_address in destination_addresses:
            destination_to_deposits[destination_address] = deposit_address

r = requests.get(JOBCOIN_API + '/addresses/' + MIXER_ADDRESS)
mixer_balance = r.json()['balance']
transactions = r.json()['transactions']

if Decimal(mixer_balance) <= 0:
    completed = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    with open(JOB_SEND_FROM_LOG, 'a') as f:
        log_line = "[%s] Job Send From Mixer Completed.  Empty Balance: %s.\n" % (completed, mixer_balance)
        print log_line
        f.write(log_line)
    import sys
    sys.exit()
"""
  3. Compute totals:
"""

deposit_totals = {}
dispersal_totals = {}
for transaction in transactions:
    amount = transaction['amount']
    to_address = transaction['toAddress']
    from_address = ''
    if 'fromAddress' in transaction:
        from_address = transaction['fromAddress']

    if from_address in deposit_to_destinations:
        if from_address not in deposit_totals:
            deposit_totals[from_address] = Decimal('0.0')
            dispersal_totals[from_address] = Decimal('0.0')
        deposit_totals[from_address] += Decimal(amount)
    """
      Feels like a slight comment here couldn't hurt.

      IF this is a transaction from the Mixer to a known destination,
      THEN we get the associated deposit address and add the amount to that.
    """
    if from_address == MIXER_ADDRESS and to_address in destination_to_deposits:
        deposit_address = destination_to_deposits[to_address]
        dispersal_totals[deposit_address] += Decimal(amount)
"""
  3B. Persist current totals to database.
"""
with con:
    """
      Yes, maybe a little ugly, but it works.
    """
    sql = ""
    for deposit_address in deposit_totals:
        idx = index_from_deposit_address(deposit_address)
        sent_to = str(deposit_totals[deposit_address])
        sent_from = str(dispersal_totals[deposit_address])

        sql += """
          UPDATE
            addresses
          SET
            total_sent_to_mixer = '%s',
            total_sent_from_mixer = '%s'
          WHERE deposit_address_id = %d;
        """ % (sent_to, sent_from, idx)

    if sql:
        con.executescript(sql)
"""
  4. Compute remainders:
"""
remainders = {}
for deposit_address in deposit_totals:
    remainder = deposit_totals[deposit_address] - dispersal_totals[deposit_address]
    if remainder >= Decimal(DISPERSAL_UNIT):
        remainders[deposit_address] = remainder
"""
  5. Disperse some of the remainders to an appropriate destinations.
"""
for deposit_address in remainders:
    remainder = remainders[deposit_address]

    print "deposit_address: %s, remainder: %s, destinations: %s" % (deposit_address, remainder, deposit_to_destinations[deposit_address])

    destinations = deposit_to_destinations[deposit_address]
    random.shuffle(destinations)
    while destinations and remainder >= Decimal(DISPERSAL_UNIT):
        to_address = destinations.pop()
        payload = {'fromAddress': MIXER_ADDRESS, 'toAddress': to_address, 'amount': DISPERSAL_UNIT}
        print "\tSending Payload: %s" % (payload)
        r = requests.post(JOBCOIN_API + '/transactions', params=payload)
        if r.status_code == 200:
            remainder -= Decimal(DISPERSAL_UNIT)
            total_dispersed += Decimal(DISPERSAL_UNIT)

completed = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
with open(JOB_SEND_FROM_LOG, 'a') as f:
    log_line = "[%s] Job Send From Mixer Completed.  Total Jobcoins Dispersed: %s.\n" % (completed, str(total_dispersed))
    print log_line
    f.write(log_line)
