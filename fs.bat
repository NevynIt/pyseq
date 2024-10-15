@echo off

call .venv\Scripts\activate.bat
@REM Call the Python script and capture its output
for /F %%i in ('py examples/get_fs_port_n.py') do set fs_port_n=%%i

cd C:\FluidSynth\
fluidsynth FluidR3_GM.sf2 -o midi.winmidi.device=%fs_port_n%
cd c:\Stuff\pyseq