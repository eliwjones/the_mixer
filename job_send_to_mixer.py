import requests
import sqlite3
from conf import DATABASE, JOBCOIN_API, JOB_SEND_TO_LOG, MIXER_ADDRESS
from conf import deposit_address_from_index
from datetime import datetime

started = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
with open(JOB_SEND_TO_LOG, 'a') as f:
    log_line = "[%s] Job Send To Mixer Started.\n" % (started)
    f.write(log_line)

con = sqlite3.connect(DATABASE)

total_sweeped = 0
deposit_addresses = []
with con:
    for row in con.execute("SELECT deposit_address_id FROM addresses"):
        deposit_address = deposit_address_from_index(row[0])
        deposit_addresses.append(deposit_address)

for deposit_address in deposit_addresses:
    r = requests.get(JOBCOIN_API + '/addresses/' + deposit_address)

    balance = r.json()['balance']
    if int(balance) <= 0:
        print "%s has '0' balance.  Continuing." % (deposit_address)
        continue

    print "Transferring %s to '%s' for '%s'." % (balance, MIXER_ADDRESS, deposit_address)
    payload = {'fromAddress': deposit_address, 'toAddress': MIXER_ADDRESS, 'amount': balance}

    r = requests.post(JOBCOIN_API + '/transactions', params=payload)
    if r.status_code == 200:
        total_sweeped += int(balance)
    """
    NOTE: We don't really care if the transaction fails, next run will try again
            with whatever new balance is.

          For a real setup, we'd report on 422's and other non-2XX status codes (and
          exceptions) to keep a sense of how things were doing.

          Also, batching would be much nicer, but Jobcoin does not seem to support that.
    """

completed = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
with open(JOB_SEND_TO_LOG, 'a') as f:
    log_line = "[%s] Job Send To Mixer Completed.  Total Jobcoins Sweeped: %s.\n" % (completed, total_sweeped)
    f.write(log_line)
