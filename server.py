#!/usr/bin/env python3

import http.server

PORT = 8000
httpd = http.server.HTTPServer( ("", PORT), http.server.CGIHTTPRequestHandler)
try:
		print ("Server started at port:", PORT)
		httpd.serve_forever()
except KeyboardInterrupt:
		print('\nShutting down server')
		httpd.socket.close()