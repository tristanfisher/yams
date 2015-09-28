# YAMS 
#### Y(et) A(nother) M(anagement) S(ystem)

[![Build Status](https://travis-ci.org/tristanfisher/yams.svg?branch=master)](https://travis-ci.org/tristanfisher/yams)

### What does it do?

YAMS aims to be an easy-to-use extensible interface for maintaining and monitoring system infrastructures.

### Installation

YAMS relies on Python 3.5 and runs on Linux or OS X.  Activate a virtual environment and install the requirements from the requirements.txt.

### Communication

YAMS runs on the following ports:

| Port 	| Transport Protocol 	| Application Protocol 	| Usage           	|
|------	|--------------------	|----------------------	|-----------------	|
| 1110 	| TCP                	| HTTP(S)              	| YAMS Frontend   	|
| 1111 	| TCP                	| HTTP(S)              	| YAMS REST API   	|
| 1112 	| UDP/TCP            	| YAMS Socket          	| YAMS Socket API 	|

While running on the built-in development server is fine for feature development or very small installations, the use of uWSGI and a reverse proxy (such as via nginx) is heavily recommended.  This is also the preferred method of running YAMS on more predictable ports, such as TCP:443 for the YAMS frontend.

### Project Layout/Architecture

YAMS is split into two main folders, ***yams-api/*** and ***yams/***.

***yams-api/*** 

The RESTful API component of YAMS.

***yams/*** 

The front-end management GUI, user dashboard, and web interface of YAMS.  


### Adding Functionality

To add front-end code, use the `yams/static/plugins/custom` folder.  This is a special directory that will not be changed in future releases.

To add back-end code, place a Python module with relevant Flask routes in `yams_api/<< version >>` and name it `views.py`.

e.g. 

`yams_api/dev/github/views.py`:

```python
from flask import jsonify
from yams_api.dev import dev_bp

@dev_bp.route('/github')
def github():
    return jsonify(status="ok")
```

When you restart YAMS (or YAMS API), your `views.py` file will be automagically included.
 

### Contributing

Please fork the repo, switch to the dev branch (or master/release for documentation), make your changes, and submit a pull request (`git rebase` first please).


#### Code

All code submissions should be done through pull requests.  If you're feeling extra nice (and want to increase the chances of a merge), include unittests.

Please place candidate front-end plugins in the `yams/static/extras/` directory.

Please place candidate back-end plugins in the `/dev/plugins/` directory.

If the change is large, please make sure that it is well-commented and be patient.

#### Documentation

If something is poorly explained and you feel it should be better, please either open a GitHub issue or make a pull request with documentation against the branch that contains the object you're writing about. 

e.g. "user permissions on branch dev" -> dev branch

#### Bug Hunters

If you find a bug in YAMS, please open a GitHub issue with the description of the bug, the version you're running, and any information you think may be helpful.

Please note that all fixes will be rolled forward into newer releases.



---
 
######*Tristan Fisher 2015*
