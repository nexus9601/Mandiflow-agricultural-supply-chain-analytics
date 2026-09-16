"""
MandiFlow | Agricultural Supply Chain Analytics
Streamlit Entry Point Shim

Supports deployments pointing to either 'app.py' or 'streamlit_app.py'.
"""
import runpy
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

_target = os.path.join(_HERE, "streamlit_app", "streamlit_app.py")
if not os.path.exists(_target):
    _target = os.path.join(_HERE, "streamlit_app.py")
runpy.run_path(_target, run_name="__main__")
