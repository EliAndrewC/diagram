import re, urllib.parse

def norm(u):
    u = u.strip().strip("'\"<>),.;")
    u = urllib.parse.unquote(u)
    u = u.split("#")[0]
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = re.sub(r"^([a-z]{2,3})\.m\.wikipedia", r"\1.wikipedia", u)
    u = re.sub(r"^m\.", "", u)
    u = u.rstrip("/")
    return u.lower() if "wikipedia" not in u else u[: u.find("/")].lower() + u[u.find("/"):] if "/" in u else u.lower()


