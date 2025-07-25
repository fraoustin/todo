# Todo

sample of todo application with fastapi and nicegui

## installation

> pip install -r REQUIREMENTS.txt

## run

> mkdir data
> python app/main.py

## quality

correction quality

> autopep8 --in-place --recursive app/*

check quality

> flake8

## tests

> python tests/run_tests.py

## todo

ajout langue i18n


ajout gestion filtre groupe dans login_

il faudrait traiter les erreur d'api en les mettant aussi dans une langue demandée

faire un Dockerfile (mais correct sans le .git et avec un alpine et les bons utilisateurs)

faire explication sur doc perso du fonctionnement
