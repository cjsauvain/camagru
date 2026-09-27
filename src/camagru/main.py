from camagru.db.init import init
from camagru.lib.overlays import load
from camagru.server import serve


def main():
    init()
    load()
    serve()
