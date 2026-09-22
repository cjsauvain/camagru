from camagru.lib.request import Request
from camagru.lib.response import clear_cookie, redirect
from camagru.services.auth import logout_user


def logout(request: Request) -> tuple[str, list, bytes]:
    logout_user(request.cookies.get("session"))
    
    return redirect("/gallery", [clear_cookie("session")])