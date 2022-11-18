
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

def test_app(environ, start_response):
    status = "200 OK"  # HTTP Status
    headers = [("Content-type", "text/plain; charset=utf-8")]  # HTTP Headers
    start_response(status, headers)

    wsgi_input = environ["wsgi.input"]
    b = wsgi_input.read(int(environ["CONTENT_LENGTH"]))
    s = b.decode("utf-8")
    print(parse_qs(s))
    return [b"Hello World !"]

with make_server('', 8000, test_app) as httpd:
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    httpd.serve_forever()
