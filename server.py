# coding: utf-8

# Copyright 2014 Abram Hindle, Eddie Antonio Santos, Rooshil Patel
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
# https://docs.python.org/2/library/os.html
# https://docs.python.org/2/library/time.html
# https://docs.python.org/2/library/mimetypes.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

import SocketServer
import os
import time
import mimetypes

WEB_SERVER_DIR = "/www"

class MyWebServer(SocketServer.BaseRequestHandler):
    
    #Method generates response to send back to requesting client
    #Able to either generate 200, 301 or 404 responses
    def generate_response(self, request_path):
        response = ""
        
        #Checks and prevents attempts at path traversal
        if "/../" in request_path:
            response = self.not_found()
            return response
        #Redirects /deep to /deep/ as per eclass discussion https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=441938
        elif request_path == "/deep":
            response = self.redirect("/deep/")
            return response

        actual_path = os.getcwd() + WEB_SERVER_DIR + request_path

        #determines if the path points to a file
        if os.path.isfile(actual_path):
            response = self.ok_file(actual_path)
            return response
        
        #determines if the path points to a directory
        elif os.path.isdir(actual_path):
            actual_path += "index.html"
            response = self.ok_file(actual_path)
            return response
        else:
            response = self.not_found()
            return response
    
    #generates 200 OK header and attaches file content to be sent
    def ok_file(self, file_path):
        #determines mimetype for file to be served
        mime_type = mimetypes.guess_type(file_path)
        header = ("HTTP/1.1 200 OK\r\n" + 
                 "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()) + "\r\n" + 
                 "Content-Type: " + mime_type[0] + "\r\n\r\n")
        
        file_open = open(file_path, "r")
        header += file_open.read()
        file_open.close()
        return header

    #generates 301 Moved Permanently header using location provided
    def redirect(self, location):
        header = ("HTTP/1.1 301 Moved Permanently\r\n" + 
                 "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()) + "\r\n" + 
                 "Location: http://127.0.0.1:8080" + location + "\r\n\r\n")
        return header

    #generates 404 not found header
    def not_found(self):
        header = ("HTTP/1.1 404 Not Found\r\n" +
                 "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()) + "\r\n" +
                 "Content-Type: text/html\r\n\r\n" + 
                 "<!DOCTYPE html>\n" +
                 "<html><body>\n" + "<h1>404: Not Found</h1>\n" + "</body></html>")
        return header

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of:\n%s\n" % self.data)

        #parses request
        http_request = self.data.split("\r\n")
        request_path = http_request[0].split()
        response = self.generate_response(request_path[1])
        print("Responding request with:\n%s\n" % response)
        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
