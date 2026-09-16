@echo off
REM Launch the Connect Four demo without activating the venv first.
REM Double-click this, or run `play` from the repo root.
cd /d "%~dp0"
.venv\Scripts\connect4.exe %*
pause