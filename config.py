class BaseConfig(object):
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	DEBUG = False
	TESTING = False
	SQLALCHEMY_ECHO = False # show sql commands

	HOST="0.0.0.0"
	PORT=5000

	LOGIN="user"
	PASSWORD="password"

class TestingConfig(BaseConfig):
	TESTING = True
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/jd_testing'

class DevelopmentConfig(BaseConfig):
	DEBUG = True
	SQLALCHEMY_ECHO = True
	SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/jd_development'

class ProductionConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/jd_production'
