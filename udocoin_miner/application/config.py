import os,pathlib,json

class Config(object):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = False
    SECRET_KEY = "my-not-so-secret-secret"

class ProductionConfig(Config):
    SECRET_KEY = os.urandom(12).hex()

class DevelopmentConfig(Config):
    TESTING = True
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True