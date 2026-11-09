from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

"""
This file contains a simple HTTP server implementation that can be used for testing.
This service is not part of the official HSL3 documentation and is only used for testing purposes.
"""


def simple_http_server(callback = None, port: int=8080):
    """ 
    Run a simple HTTP server.
    - callback: function to be called with POST data (as str) on POST.
    - port: which port to listen on (default 8080).
    
    Returns: (httpd, thread)
    """
    class CustomHandler(SimpleHTTPRequestHandler):
        pass

    CustomHandler.callback = callback

    server = HTTPServer(("", port), CustomHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    callback = None

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Hello, world! This is a GET response.\n")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
        if self.callback:
            self.callback(self.headers, post_data)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"POST request received.\n")