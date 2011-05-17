#!/usr/bin/python26

# Imports
from wsgiref.simple_server import make_server
import json

# Handle GET requests
def HandleGet(sRemoteUser, sPath):
    if sPath == "/configuration":
        return HandleGetConfiguration(sRemoteUser);
    else:
        raise Exception("Unknown path: " + sPath);

# Handle GET configuration request
def HandleGetConfiguration(sRemoteUser):
    supportedoperations = ["Add",
                           "Evaporate",
                           "Transfer",
                           "Elute",
                           "React",
                           "Prompt",
                           "Install",
                           "Comment",
                           "Activity"];
    config = {"type":"configuration",
              "name":"Mini cell 3",
              "version":"2.0",
              "debug":"false",
              "supportedoperations":supportedoperations};
    return config;

# Handle POST requests
def HandlePost(user, path):
    return "POST"

# Handle DELETE requests
def HandleDelete(user, path):
    return "DELETE"

# Main WSGI application entry point
def application(environ, start_response):
    # Extract important input variables
    sRemoteUser = environ["REMOTE_USER"]
    sRequestMethod = environ["REQUEST_METHOD"]
    sPath = environ["PATH_INFO"]

    # Handle the request
    try:
        # Call the appropriate handler
        if sRequestMethod == "GET":
            sResponse = HandleGet(sRemoteUser, sPath)
        elif sRequestMethod == "POST":
            sResponse = HandlePost(sRemoteUser, sPath)
        elif sRequestMethod == "DELETE":
            sResponse = HandleDelete(sRemoteUser, sPath)
        else:
            raise Exception, "Unknown request method"
    except Exception as ex:
        # Send an error message back to the client
        sResponse = {"type":"error","description":str(ex)}

    # Initialize the return status and headers
    sStatus = "200 OK"
    sResponseJSON = json.dumps(sResponse)
    pHeaders = [("Content-type", "text/plain"), ("Content-length", str(len(sResponseJSON)))]

    # Send the response
    start_response(sStatus, pHeaders)
    return sResponseJSON

# Main function used for local execution
if __name__ == '__main__':
    httpd = make_server('', 80, application)
    print "Serving on port 80..."
    httpd.serve_forever()

