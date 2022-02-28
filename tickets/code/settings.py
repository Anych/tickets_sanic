import os

DATABASE_URL = os.environ['DATABASE_URL']
DEBUG = os.environ['DEBUG']
REDIS_URL = os.environ['REDIS_URL']
SEARCH_EXPIRE_TIME = 20 * 60
TEST_DATABASE_URL = 'postgres://postgres:123@postgres:5432/postgres?sslmode=disable'
