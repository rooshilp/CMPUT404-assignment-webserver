# coding: utf-8

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

import SocketServer
import os
import time
import mimetypes

WEB_SERVER_DIR = "./www"

class MyWebServer(SocketServer.BaseRequestHandler):
    
    def generate_response(self, request_path):
        response = ""
        if "/../" in request_path:
            response = self.not_found()
            return response
        elif request_path == "/deep":
            response = self.redirect("/deep/")
            return response

        actual_path = os.getcwd() + WEB_SERVER_DIR + request_path

        if os.path.isfile(actual_path):
            response = self.ok_file(actual_path)
            return response
        
        elif os.path.isdir(actual_path):
            actual_path += "index.html"
            response = self.ok_file(actual_path)
            return response
        else:
            response = self.not_found()
            return response

    def ok_file(self, file_path):
        mime_type = mimetypes.guess_type(file_path)
        header = ("HTTP/1.1 200 OK\r\n" + 
                 "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()) + "\r\n" + 
                 "Content-Type: " + mime_type + "\r\n\r\n")
        
        file_open = open(file_path, "r")
        header += file_open.read()
        file_open.close()
        return header

    def redirect(self, location):
        header = ("HTTP/1.1 301 Moved Permanently\r\n" + 
                 "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()) + "\r\n" + 
                 "Location: http://127.0.0.1:8080" + location + "\r\n\r\n")
        return header

    def not_found(self):
        header = ("HTTP/1.1 404 Not Found\r\n" +
                 "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime()) + "\r\n" +
                 "Content-Type: text/html\r\n\r\n" + 
                 "<!DOCTYPE html>\n" +
                 "<html><body>\n" + "<h1>404: Not Found</h1>\n" + "</body></html>")
        return header

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        http_request = self.data.split("\r\n")
        request_path = http_request[0].split()

        response = self.generate_response(request_path[1])
        self.request.sendall(response)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
