@echo off
echo.
echo  MandiFlow - Agricultural Supply Chain Analytics
echo  Starting Streamlit Dashboard...
echo.
cd /d "%~dp0"
streamlit run streamlit_app\mandiflow_app.py --server.port 8501 --browser.gatherUsageStats false
