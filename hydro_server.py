import http.server
import socketserver

PORT = 8000
#Handler = http.server.CGIHTTPRequestHandler

class Handler(http.server.CGIHTTPRequestHandler):
    cgi_directories = ["/cgi-bin"]

#with http.server.HTTPServer(("", PORT), Handler) as httpd:
with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
	print("serving at port", PORT)
	httpd.serve_forever()

