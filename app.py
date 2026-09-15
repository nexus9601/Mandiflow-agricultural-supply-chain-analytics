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

runpy.run_path(os.path.join(_HERE, "streamlit_app.py"), run_name="__main__")
