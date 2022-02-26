import os
import sys

from pytest import fixture

from sanic import Sanic

PROJECT_ROOT = os.path.abspath(os.path.join(
                  os.path.dirname(__file__),
                  os.pardir))
sys.path.insert(0, PROJECT_ROOT)


@fixture
def app():
    from code import app as sanic_app

    test_app = Sanic('test-app')
    test_app.router = sanic_app.app.router
    return test_app
