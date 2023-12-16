@echo off
python main.py examples/%1.hl -o examples/%1.exe
if (%ERRORLEVEL% == 0) (
	exit
) else (
	cd examples
	%1.exe
	cd ..
)
