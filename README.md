# Westeaker

Westeaker is a web application for generating, transpiling, composing, and executing Grover quantum circuits using Qiskit. It supports both whole-program transpilation and a fragment-based approach in which independently transpiled circuit components are reused and composed to construct complete executable Grover circuits.

The project is divided into two applications:

```text
westeaker/
├── be/   # FastAPI + Qiskit backend
└── fe/   # Angular frontend
```

## Requirements

### Backend

- Python 3
- Qiskit and the Python dependencies required by the backend

### Frontend

- Node.js
- npm
- Angular CLI

## Configure `root_folder`

Westeaker stores generated fragments, composed Grover circuits, whole Grover circuits, and execution results under the directory configured by `Folders.root_folder`.

The configuration is located in:

```text
be/app/quantum/Folders.py
```

For example:

```python
from pathlib import Path
class Folders:
    root_folder = Path.home() / "Desktop" / "westeakers" / "web"
```

This automatically resolves the user's home directory. For example, on macOS it will resolve to:

```text
/Users/<user>/Desktop/westeakers/web
```

and on Ubuntu to:

```text
/home/<user>/Desktop/westeakers/web
```

Create the directory before starting Westeaker if it does not already exist:

```bash
mkdir -p ~/Desktop/westeakers/web
```

To use another location, change `root_folder`, for example:

```python
root_folder = Path("/opt/westeaker/results/web")
```

The user running the backend must have read and write permissions on this directory.

## Start the backend

Go to the backend directory:

```bash
cd be
```

Activate the Python virtual environment. For example:

```bash
source .venv/bin/activate
```

or activate the environment where Qiskit and the backend dependencies are installed.

Start FastAPI with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

API health check:

```text
http://localhost:8000/api/health
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

## Start the frontend

Open another terminal and go to the frontend directory:

```bash
cd fe
```

Install dependencies the first time:

```bash
npm install
```

Start Angular:

```bash
ng serve
```

The frontend will be available at:

```text
http://localhost:4200
```

The development environment expects the backend at:

```text
http://localhost:8000/api
```

## Production build

Build the Angular application with:

```bash
cd fe
ng build --configuration production
```

The production Angular environment should use:

```typescript
export const environment = {
  production: true,
  apiUrl: '/api'
};
```

This allows the frontend and backend to be served from the same host and port.

For a deployment where FastAPI also serves the compiled Angular application, Westeaker can be started on port `8522` with:

```bash
cd be
uvicorn app.main:app --host 0.0.0.0 --port 8522
```

The application will then be accessible at:

```text
http://<server>:8522/
```

and the API at:

```text
http://<server>:8522/api/
```

## Main generated data

Under `root_folder`, Westeaker may create directories such as:

```text
web/
├── fragments/
├── composed_grovers/
├── whole_grovers/
└── results.tsv
```

- `fragments/`: generated and transpiled circuit fragments.
- `composed_grovers/`: Grover circuits assembled from transpiled fragments.
- `whole_grovers/`: complete Grover circuits generated/transpiled as a whole.
- `results.tsv`: generation, transpilation, and execution results.

## Typical development workflow

Start the backend:

```bash
cd be
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then, in another terminal, start the frontend:

```bash
cd fe
ng serve
```

Open:

```text
http://localhost:4200
```
