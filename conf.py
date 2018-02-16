DATABASE = 'mixer.db'
SCHEMA_FILENAME = 'mixer_schema.sql'
JOBCOIN_API = 'http://jobcoin.gemini.com/handled/api'

DEPOSIT_ADDRESS_PREFIX = 'mixer-'
MIXER_ADDRESS = 'the-tent'
DISPERSAL_UNIT = '0.5'

JOB_SEND_TO_LOG = 'job_send_to_mixer.log'
JOB_SEND_FROM_LOG = 'job_send_from_mixer.log'

def deposit_address_from_index(idx):
    return "%s%d" % (DEPOSIT_ADDRESS_PREFIX, idx)

def index_from_deposit_address(addr):
    idx = ""
    if addr.startswith(DEPOSIT_ADDRESS_PREFIX):
        idx = addr[len(DEPOSIT_ADDRESS_PREFIX):]
    return int(idx)