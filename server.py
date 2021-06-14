import http.server
import socketserver
import autocomplete
import urllib.parse as parse
import signal
import sys
import time
import os
import multiprocessing as mp
import pandas

if __name__ == "__main__":
    
    PORT = 8000
    results = pandas.read_csv("parmenides_results.csv")
    print("Results:", len(results))
    splits = []
    num_threads = max(os.cpu_count(), mp.cpu_count())
    len_results = len(results)

    for i in range(num_threads):
        start = int(i * len_results / num_threads)
        end = int((i + 1) * len_results / num_threads)
        splits.append(results[start:end])

    with mp.Pool(num_threads) as p:
        class AutocompleteServer(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "text/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                search_terms = parse.unquote(self.path[1:])
                self.wfile.write(
                    bytes(autocomplete.search_json(search_terms, splits, p), "utf-8")
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
