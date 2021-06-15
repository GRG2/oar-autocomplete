'''
Noah Hobson, nhobs1999@gmail.com
simple_http.py

All this program does is run a simple http server. It listens for requests and grants them.
It uses the current directory as its target for serving web pages.
This should NOT be used in final production because it is:
a) Unsafe (only makes the most basic checks internally, and is not encrypted)
b) Poorly made (and would not respond well to heavy load)
c) Naive
However, for a demo, it will be perfectly fine.
'''

import http.server
import socketserver

PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

while True:
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()
    except KeyboardInterrupt:
        break