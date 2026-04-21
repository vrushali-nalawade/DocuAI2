#!/bin/bash

apt-get update
apt-get install -y tesseract-ocr

uvicorn src.main:app --host 0.0.0.0 --port 10000
