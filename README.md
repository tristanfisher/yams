# YAMS 
#### Y(et) A(nother) M(anagement) S(ystem)


### What does it do?

YAMS aims to be an easy-to-use extensible interface for maintaining and monitoring system infrastructures.


### Usage

YAMS runs on TCP port 5000 for the web interface and (optionally) TCP port 5001 for the stand-alone API.  Over time, the YAMS front-end will likely depend on the YAMS API running.

While running on the built-in development server is fine for feature development or very small installations, the use of uWSGI and a reverse proxy (such as via nginx) is heavily recommended.

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