import os
from pip.req import parse_requirements

from version import version

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

main_script = "run.py"
api_script = "run_api.py"

install_requirements = parse_requirements("./requirements.txt", session=False)
install_requirements = [str(ir.req) for ir in install_requirements]

setup(
    name = "yams",
    version = version,
    author = "Tristan Fisher",
    author_email = "code@tristanfisher.com",
    description = "Yet Another Management System",
    long_description = open(os.path.join(os.path.realpath(os.path.dirname(__file__)), "README.md"), "r").read(),
    scripts = [main_script, api_script],
    url =  "http://github.com/tristanfisher/yams",
    license = open("LICENSE").read(),
    install_requires = install_requirements,
    setup_requires = []
)
