from http.server import BaseHTTPRequestHandler
from generate_agricultural_data import generate_html_content

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = generate_html_content()
        self.wfile.write(html_content.encode())
        return