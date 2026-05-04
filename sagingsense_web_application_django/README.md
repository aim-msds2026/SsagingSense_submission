# SagingSense Django Version 2

**Project Title:** SagingSense: An Integrated System for Banana Ripeness Classification and Banana Leaf Disease Screening

This Django MTV web application now supports two independent modules:
- banana ripeness classification
- banana leaf disease classification

Each module has its own upload page, model loader, labels file, metadata file, and recommendation logic.

## Model asset folders

### Ripeness module

Place these files inside:

```text
predictor/model_assets/ripeness/
```

Required files:

```text
sagingsense_best_model.keras
class_labels.json
model_metadata.json
```

### Leaf disease module

Place these files inside:

```text
predictor/model_assets/leaf_disease/
```

Required files:

```text
banana_leaf_disease_best_model.keras
class_labels.json
model_metadata.json
```

## Installation

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Command Prompt

```cmd
python -m venv .venv
.venv\Scriptsctivate.bat
```

### Mac or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run migrations

```bash
python manage.py migrate
```

### Start the app

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Notes

- The app opens even if one or both trained model files are missing.
- Each scanner page will show a setup message if its model file has not yet been copied into the correct folder.
- The app resizes uploads using the `image_size` stored in each module's `model_metadata.json`.

## Project structure

```text
sagingsense_django_project/
├── manage.py
├── requirements.txt
├── README.md
├── sagingsense/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── predictor/
    ├── forms.py
    ├── utils.py
    ├── views.py
    ├── urls.py
    ├── model_assets/
    │   ├── ripeness/
    │   │   ├── sagingsense_best_model.keras
    │   │   ├── class_labels.json
    │   │   └── model_metadata.json
    │   └── leaf_disease/
    │       ├── banana_leaf_disease_best_model.keras
    │       ├── class_labels.json
    │       └── model_metadata.json
    ├── static/predictor/css/styles.css
    └── templates/predictor/
        ├── base.html
        ├── home.html
        ├── scanner.html
        └── result.html
```

Created by: Bob Mathew Sunga
