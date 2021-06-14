import http.server
import socketserver
import autocomplete
import urllib.parse as parse
import signal
import sys
import time

if __name__ == "__main__":
    PORT = 8000

    class AutocompleteServer(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(
                bytes(autocomplete.search_json(parse.unquote(self.path[1:])), "utf-8")
            )

    # https://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
    def signal_handler(sig, frame):
        global server
        print("Received ctrl+c, exiting...")
        server.server_close()
        time.sleep(3)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    server = None
    while server == None:
        try:
            server = socketserver.ThreadingTCPServer(("", PORT), AutocompleteServer)
        except:
            pass
    server.allow_reuse_address = True
    server.daemon_threads = True

    try:
        while True:
            print("Serving on port", PORT)
            sys.stdout.flush()
            server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
