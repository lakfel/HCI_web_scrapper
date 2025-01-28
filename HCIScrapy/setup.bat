@echo off
echo Installing Python dependencies...

REM Check if pip is installed
python -m pip --version
if errorlevel 1 (
	echo Installing pip...
	python -m ensurepip --default-pip
)

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
python -m pip install -r requirements.txt

echo Installation complete!
pause