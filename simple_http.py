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