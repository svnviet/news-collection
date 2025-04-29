from flask import Flask


class Swagger:
    def __init__(self, app: Flask):
        self.app = app
        self.url = app.config["SWAGGER_URL"]
        self.__name__ = "Flask"
        self.__version__ = app.config["VERSION"]
        self.__title__ = "Flask API"

