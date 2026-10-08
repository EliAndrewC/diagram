"""The CodeBuild dispatcher (feature 130): when a remote run is permitted, and how it is driven.

See CLAUDE.md in this directory for the module map, the one rate constant, the five dispatch
conditions and the threat model. Every entry here is reached through `make ci-*`; `__main__.py`
refuses anything else.
"""
