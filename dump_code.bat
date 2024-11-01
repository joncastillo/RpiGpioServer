@echo off
set "output=code_dump.txt"
if exist %output% del %output%

for /r %%f in (*.cu *.cuh *.c *.cpp *.h *.hpp *.py) do (
    rem Check if the file path contains excluded directories
    echo %%f | findstr /i "\\Lib\\ \\Scripts\\ \\x64\\ \\." >nul
    if errorlevel 1 (
        echo **%%f**: >> %output%
        echo ```cpp >> %output%
        type "%%f" >> %output%
        echo. >> %output%
        echo ``` >> %output%
        echo. >> %output%
        echo. >> %output%
    )
)