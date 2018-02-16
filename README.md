# the_mixer
For mixing job coins.

Quick Install
=============
Prerequisites:
```
$ sudo apt-get install python-setuptools  # Linux only
$ sudo apt-get install python-pip         # Linux only
$ sudo pip install virtualenv
```

Setup the Environment:
```
$ git clone git@github.com:eliwjones/the_mixer.git
$ cd the_mixer
$ virtualenv venv --distribute
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Run API:
```
$ python app.py
```

Get A Deposit Address:
```
$ curl -i -H "Content-Type: application/json" -X POST -d '{"addresses":["secret-addr-1", "secret-addr-2"]}' http://localhost:5000/api/receive
```