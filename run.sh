#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
playwright install

export PYTHONPATH=$(pwd)
python3 tasks/wanhao_task.py