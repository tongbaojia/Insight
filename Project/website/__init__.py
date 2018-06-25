from flask import Flask

#app = Flask(__name__)

from website.audio import app

## This is how some code won't work! need specific import path
# from website import audio
# @app.route('/')
# def index():
# 	return('Hello, world')