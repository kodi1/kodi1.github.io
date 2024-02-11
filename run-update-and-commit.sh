#!/bin/bash

git pull
source .venv/Scripts/activate
python update_repo.py
deactivate
git status
git add -A
git commit -m "Automatic update"
git push