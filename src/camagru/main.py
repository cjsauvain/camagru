from camagru.db.init import init
from camagru.server import serve


def main():
    init()
    serve()
