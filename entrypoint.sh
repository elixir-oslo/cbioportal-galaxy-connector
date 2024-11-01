#!/bin/bash
source activate cbiportal-galaxy-connector
cd /server
exec uvicorn main:app --host 0.0.0.0 --port 3001 --log-level info --reload