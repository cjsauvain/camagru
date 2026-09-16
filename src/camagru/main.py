from wsgiref.simple_server import make_server


def app(environ, start_response):
    status = "200 OK"
    headers = [("Content-type", "text/plain; charset=utf-8")]
    start_response(status, headers)
    return [b"Hello from WSGI!"]


def main():
    with make_server("", 8080, app) as httpd:
        print("Serving on port 8080...")
        httpd.serve_forever()
