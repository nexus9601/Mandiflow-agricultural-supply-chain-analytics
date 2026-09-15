@echo off
echo Starting MandiFlow Streamlit Dashboard...
cd /d "%~dp0"
streamlit run streamlit_app.py --server.headless false
pause
