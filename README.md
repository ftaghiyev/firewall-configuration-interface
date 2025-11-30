# Firewall Configuration Interface

An AI-powered tool for translating natural language policy intents into vendor-specific firewall configurations (Palo Alto PAN-OS), complete with static analysis and Batfish-based network simulation.

## 🚀 Features

- **Natural Language to Policy Translation**: Describe your firewall needs in plain English (e.g., "Allow HR to access Finance servers on HTTPS").
- **Context-Aware Resolution**: Resolves zones, objects, and services from your network definition file.
- **Static Analysis (Linter)**: Validates logical correctness of the generated policy (e.g., "ICMP should not have ports").
- **Safety Gate**: Enforces security best practices (e.g., blocking 'any-any' allow rules) before generation.
- **Batfish Simulation**: Runs a "dry-run" analysis using Batfish to verify the configuration syntax and referential integrity against a simulated device.
- **Interactive UI**: Visualize the translation pipeline, validation warnings, and generated CLI commands.

## 🛠️ Architecture

The project consists of three main components:

1.  **Backend (`backend/`)**:

    - **Engine**: Core logic for intent resolution, IR building, and compilation.
    - **Safety Gate**: Pre-compilation checks for dangerous patterns (e.g. Any/Any allows).
    - **Linter**: (e.g `PaloAltoLinter`) for logical checks.
    - **Batfish Manager**: Integration with Batfish for configuration validation.
    - **API**: FastAPI server exposing endpoints for policy translation.

2.  **Frontend (`frontend/`)**:

    - React/Vite application providing a chat interface.
    - Visualizes the pipeline steps (Resolver -> IR -> Validation -> Batfish -> Config).

3.  **Batfish Service**:
    - Dockerized Batfish service for network analysis.

## 📦 Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (for Batfish)

## 🏁 Getting Started

### 1. Start Batfish Service

```bash
docker compose up -d
```

This starts the Batfish container on ports `8888` and `9996`.

### 2. Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the server:

```bash
fastapi dev src/main.py
```

The API will be available at `http://localhost:8000`.

### 3. Setup Frontend

```bash
cd frontend/interface
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`.

## 🧪 Usage

1.  Open the frontend URL.
2.  Upload a network context file (e.g., `data/prod/payroll-network.json`) or paste your network definitions (Objects, Zones).
3.  Type your policy intent in the chat (e.g., _"Allow HR_laptops to reach Finance_servers on TCP 443"_).
4.  View the generated pipeline graph:
    - **Resolver**: Shows how natural language mapped to your defined objects.
    - **IR**: The abstract rule representation.
    - **Linter**: Checks for logical errors.
    - **Safety Gate**: Checks for security violations.
    - **Batfish Analysis**: Checks for configuration validity (syntax, references).
    - **Config**: The final PAN-OS CLI commands.

## 📂 Project Structure

```
.
├── backend/                # FastAPI application
│   ├── src/engine/         # Core logic (Agents, Compiler, Linters)
│   │   ├── batfish/        # Batfish integration logic
│   │   ├── compiler/       # Vendor-specific compilers (Palo Alto)
│   │   ├── linter/         # Static linters
│   │   └── safety/         # Safety enforcement gates
│   └── routers/            # API endpoints
├── frontend/               # React application
│   └── interface/src/      # UI Components and Hooks
├── data/                   # Sample network definitions and test cases
└── docker-compose.yml      # Batfish service configuration
```

## 🛡️ Batfish Validation Details

The `BatfishManager` automatically:

- Wraps your generated firewall rules with a mock device header (interfaces, zones, virtual routers) based on your context.
- Creates dummy objects for FQDNs to bypass Batfish limitations.
- Filters out "Unused structure" noise to focus on critical errors.
- Enforces a 15-second timeout to prevent UI hangs if the service is unreachable.
