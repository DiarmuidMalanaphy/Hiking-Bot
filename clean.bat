

@echo off
set /p InputData="Enter csv file name: "
python data_cleaner.py %InputData%
echo Data cleaned.
timeout /t 1 /nobreak > NUL