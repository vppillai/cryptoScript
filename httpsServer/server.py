from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

port = 4443
httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile="ECC_prime256v1.cer", keyfile="ECC_prime256v1.key", server_side=True)

#if Mutual auth is required
#httpd.socket = ssl.wrap_socket(httpd.socket, certfile="ECC_prime256v1.cer", keyfile="ECC_prime256v1.key", server_side=True, cert_reqs=ssl.CERT_REQUIRE, ca_certs="./caCerts")

print("Server running on https://0.0.0.0:" + str(port))

httpd.serve_forever()
