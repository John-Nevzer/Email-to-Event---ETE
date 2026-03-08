@echo off
cd /d "D:\Programy\Projekty\Python\ETE"
call "D:\Programy\Projekty\Python\ETE\venv\Scripts\activate.bat"
"D:\Programy\Projekty\Python\ETE\venv\Scripts\python.exe" "D:\Programy\Projekty\Python\ETE\main.py" >> "D:\Programy\Projekty\Python\ETE\log.txt" 2>&1
