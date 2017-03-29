#!/usr/bin/env python3

PORT = 8000
import http.server
httpd = http.server.HTTPServer( ("", PORT), http.server.CGIHTTPRequestHandler)

try:
		print ("Server Started at port:", PORT)
		httpd.serve_forever()
except KeyboardInterrupt:
		print('\nShutting down server')
		httpd.socket.close()