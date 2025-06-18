# Setup Instructions

## One-Command Setup

```bash
git clone <repo-url> && cd aruco-generator && python main.py
```

## Manual Setup

1. **Clone Repository**
   ```bash
   git clone <repo-url>
   cd aruco-generator
   ```

2. **Install Dependencies** (if needed)
   ```bash
   pip install flask flask-sqlalchemy opencv-python gunicorn psycopg2-binary
   ```

3. **Run Application**
   ```bash
   python main.py
   ```

4. **Access Application**
   - Open: `http://localhost:5000`
   - Advanced mode: Full OpenCV ArUCO configuration
   - Simple mode: One-click generation

## Environment Variables (Optional)

```bash
export DATABASE_URL="postgresql://..."  # Optional PostgreSQL
export SESSION_SECRET="your-secret"     # Optional session key
export FLASK_ENV="development"          # Optional debug mode
```

## Production Deployment

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
```

## Debugging

- **Error Logs**: `debug_logs.txt`
- **AI Debug Logs**: `ai_debug_logs.txt`
- **Monitor Script**: `./debug_monitor.sh`
- **API Status**: `GET /api/debug/status`

## File Structure

```
aruco_generator/
├── aruco.py          # Core ArUCO generation
├── drawing.py        # SVG rendering
├── lightburn.py      # LightBurn export
├── web.py           # Flask routes
└── batch.py         # Batch processing

static/
└── app.js           # Frontend with error handling

templates/
└── index.html       # Main UI

app.py               # Flask configuration
main.py              # Entry point
debug_monitor.sh     # System diagnostics
```