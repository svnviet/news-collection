import logging
import time


class RequestLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        start_time = time.time()

        def logging_start_response(status, headers, *args):
            response_time = time.time() - start_time
            logging.info(f"Response Status: {status}, Duration: {response_time:.4f} seconds")
            return start_response(status, headers, *args)

        logging.info(f"Request: {environ['REQUEST_METHOD']} {environ['PATH_INFO']}")
        return self.app(environ, logging_start_response)
