@echo off

git pull
call .venv\Scripts\activate.bat
python update_repo.py
call .venv\Scripts\deactivate.bat
git status
git add -A
git commit -m "Automatic update"
git push