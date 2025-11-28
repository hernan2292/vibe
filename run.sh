#!/bin/bash
chmod +x run.sh

echo "Iniciando servidor con --reload..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
