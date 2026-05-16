#!/bin/bash

git remote set-url origin https://github.com/breachcipher/LazyFramework.git
git init
git add .
git commit -m "Update"
git branch -M main
git remote add origin https://github.com/breachcipher/LazyFramework.git
git push -u -f origin main
