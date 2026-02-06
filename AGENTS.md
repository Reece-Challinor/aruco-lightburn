# AGENTS.md - Master Guide for AI Agents

**Current Implementation**: `v2.0.0-unified`
**Last Updated**: 2025-12-26

---

## 🧭 The Prime Directive

**You are an expert software engineer working on a premium, high-performance web application.**
Your work must be **Dynamic**, **Robust**, and **Aesthetically Pleasing**.

### ❗ Critical Protocols

1.  **Golden Regulation**: The codebase is the source of truth, but `AI_NAVIGATION.xml` is your map. You MUST keep them in sync. If you modify code structure, you MUST update the corresponding line references in the XML.
2.  **Implementation Pattern**:
    -   **READ**: Check `AI_NAVIGATION.xml` to locate components.
    -   **PLAN**: Draft an `implementation_plan.md` for complex changes.
    -   **EDIT**: make changes with precision.
    -   **VALIDATE**: Run `make validate` after *every* significant change.
3.  **Documentation First**: Every file has an `<ai_agent_documentation>` header. These are NOT comments; they are structural metadata. **Update them** if you change the file's logic.
24. **Architecture Mandate**: To avoid circular imports, **ALWAYS** use Flask Blueprints for route modules. NEVER import `app` directly in a module that `app.py` imports.
    -   `app.py` -> imports `web.py` (registers blueprint)
    -   `web.py` -> imports `extensions.py` (for db), NOT `app.py`.

---

## 🗺️ Navigation & Structure

### Where is everything?
The authoritative map of the codebase is located in:
`AI_NAVIGATION.xml`

**Use this file to find:**
-   **Entry Points**: `app.py` (Flask), `core/aruco.py` (Logic).
-   **Line References**: Exact locations of classes/methods (e.g., `ArUCOGenerator` instantiation).
-   **API Structure**: Definition of backend routes and frontend clients.
-   **Data Models**: Database schema definitions.

### Key File Locations
| Component | Path | Description |
| :--- | :--- | :--- |
| **Map** | `AI_NAVIGATION.xml` | **START HERE**. The projects central nervous system. |
| **Logic** | `aruco_generator/core/aruco.py` | Core CV algorithms. Strategy pattern for Falbacks. |
| **Web** | `aruco_generator/web/web.py` | Main application routes and Blueprints. |
| **API** | `static/js/core/api.js` | Frontend API client (Class-based `ArUCOAPI`). |
| **Styles** | `static/css/main.css` | Premium styling variables and core layout. |
| **Tests** | `tests/` | Comprehensive test suite. |

---

## 🛠️ Development Workflow

We use `make` to automate the development lifecycle.

### 1. Validation (Mandatory)
Before committing ANY code, you must ensure the build passes.
```bash
make validate
```
*This runs linting (flake8), formatting checks (black), and all test suites.*

### 2. Formatting
Keep the code pretty.
```bash
make format
```
*Auto-formats Python code with `black` and `isort`.*

### 3. Testing
Run specific test suites if `make validate` is too slow for iteration.
```bash
make test             # Run all tests
make unit-test        # Core logic tests
make integration      # API/Web tests
```

---

## 🏗️ Architecture Layers

### 1. Python Backend (Flask)
-   **Pattern**: Factory Pattern (`create_app` in `app.py`).
-   **Blueprints**: Routes are modularized in `aruco_generator/web/` (e.g., `web.py`, `advanced_web.py`).
-   **DI**: Database (`db`) is initialized in extensions and imported where needed.
-   **CV Engine**: `ArUCOGenerator` handles image processing. It *gracefully degrades* if OpenCV contrib is missing.

### 2. JavaScript Frontend (Vanilla ES6+)
-   **No Build Step**: Pure ES6 modules.
-   **Entry Point**: `base.html` loads core modules.
-   **API Client**: `static/js/core/api.js` defines `APIClient` and `ArUCOAPI` classes.
    -   *Usage*: `window.arucoAPI.generatePreview(...)`
-   **State Management**: `window.appState` manages global state.

### 3. Database (SQLAlchemy)
-   **Optionality**: The app runs in "Stateless Mode" if no DB is configured.
-   **Models**: Defined in `aruco_generator/models.py`.

---

## 🤖 Common Tasks for Agents

### Adding a New Feature
1.  **Plan**: Update `implementation_plan.md`.
2.  **Backend**: Add logic to `core/aruco.py` or new module.
3.  **API**: Expose via `web/web.py` route.
4.  **Frontend**: Add method to `ArUCOAPI` class in `api.js`.
5.  **UI**: Create/Update HTML template and specific JS controller.
6.  **Docs**: Update `AI_NAVIGATION.xml` line references and file headers.
7.  **Verify**: `make validate`.

### Fixing a Bug
1.  **Reproduce**: Create a test case in `tests/`.
2.  **Fix**: Modify code.
3.  **Refine**: Run `make format`.
4.  **Verify**: Run `make test` to ensure no regression.

---

## 📝 Artifacts & Memory

-   `task.md`: Track your immediate progress.
-   `implementation_plan.md`: Propose and agree on big changes.
-   `walkthrough.md`: Show your work after it's done.

**Go forth and code brilliantly.**
