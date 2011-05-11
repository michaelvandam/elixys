#!/usr/bin/python

from wsgiref.simple_server import make_server

def application(environ, start_response):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'text/plain')] # HTTP Headers
    start_response(status, headers)

    # The returned object is going to be printed
    return ["Hello World"]

if __name__ == '__main__':
    httpd = make_server('', 80, hello_world_app)
    print "Serving on port 80..."
    httpd.serve_forever()
