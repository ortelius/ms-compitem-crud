#!/bin/bash

uvicorn --host 0.0.0.0 --port 5000 main:app &
pid1=$!
sleep 10
curl -s http://127.0.0.1:5000/openapi.json | jq "." >openapi.json
kill $pid1
