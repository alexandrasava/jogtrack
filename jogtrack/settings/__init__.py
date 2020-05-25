from .base import *

try:
    from .local import *
    live = False
except Exception as e:
    live = True

if live:
    from .production import *
