The Mixer
=========
For mixing job coins.

Quick Install
=============
Prerequisites:
```
$ sudo apt-get install python-setuptools  # Linux only
$ sudo apt-get install python-pip         # Linux only
$ sudo easy_install pip                   # OS X only
$ sudo pip install virtualenv
```

Setup the Environment:
```
$ git clone git@github.com:eliwjones/the_mixer.git
$ cd the_mixer
$ virtualenv venv --distribute
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Run API:
```
$ source venv/bin/activate
(venv) $ python app.py
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 219-492-209
```

Get A Deposit Address:
```
$ curl -i -H "Content-Type: application/json" -X POST -d '{"addresses":["secret-addr-1", "secret-addr-2"]}' http://localhost:5000/api/receive
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 35
Server: Werkzeug/0.14.1 Python/2.7.10
Date: Fri, 16 Feb 2018 23:38:47 GMT

{
  "deposit_address": "mixer-10"
}
```

Send Some Jobcoin (from Alice) to it:
```
$ curl -i -X POST 'http://jobcoin.gemini.com/handled/api/transactions?fromAddress=Alice&toAddress=mixer-10&amount=5'
```

Run Jobs to move the Jobcoins around:
=====================================
```
$ source venv/bin/activate
(venv) $ python job_send_to_mixer.py 
mixer-1 has '0' balance.  Continuing.
  .
  .
  .
mixer-12 has '0' balance.  Continuing.


(venv) $ python job_send_from_mixer.py 
[2018-02-16 18:53:18] Job Send From Mixer Started.

deposit_address: mixer-1, remainder: 60.0, destinations: [u'secret-addr-3', u'secret-addr-4']
	Sending Payload: {'amount': '0.5', 'fromAddress': 'the-tent', 'toAddress': u'secret-addr-3'}
	Sending Payload: {'amount': '0.5', 'fromAddress': 'the-tent', 'toAddress': u'secret-addr-4'}
[2018-02-16 18:53:20] Job Send From Mixer Completed.  Total Jobcoins Dispersed: 1.0.
```

NOTES:
======
* I haven't broken the code out into functions as this gives me a sense of how complex/heavy the architecture feels with everything unrolled.
* Though, it is indeed time to break things out into functions and add tests (in the least, integration tests)
* I feel like I overdid it with the unique destination_address, but was too annoyed to have that bug hiding in there.
