<!--
<ai_agent_documentation>
  <file_meta>
    <name>ERROR_HANDLING.md</name>
    <version>1.1.0</version>
    <type>error_handling_guide</type>
    <purpose>Standard error handling patterns for API routes</purpose>
    <last_updated>2026-02-08</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Error Handling Patterns

## API Response Envelope
All calibration and validation endpoints return a unified JSON envelope.

Success:
```
{
  "success": true,
  "data": { ... },
  "warnings": [{ "code": "db_disabled", "message": "..." }],
  "request_id": "req_...",
  "timestamp": "2026-02-08T12:00:00Z",
  "version": "2.3.0"
}
```

Error:
```
{
  "success": false,
  "error": {
    "message": "Human-friendly error",
    "type": "validation_error",
    "status": 400,
    "fields": { "square_size_mm": "Must be > 0" },
    "suggestions": ["4X4_50", "4X4_100"]
  },
  "request_id": "req_...",
  "timestamp": "2026-02-08T12:00:00Z",
  "version": "2.3.0"
}
```

## API Validation
- Validate inputs early and return `400` with actionable messages.
- Provide per-field errors in the `error.fields` map.
- Include `suggestions` when a small list of valid values exists.
- Use shared helpers in `aruco_generator/core/utils.py` where possible.

## Server Errors
- Wrap API handlers with `handle_api_errors` to standardize `500` responses.
- Log stack traces on server, return user-safe messages to clients.

## Database Optionality
- Treat DB persistence as optional. Guard writes with `current_app.config["USE_DB"]`.
- If DB is disabled, return success with a warning indicating metrics were not persisted.

## Anti-patterns
- Generic “check your parameters” messages without context.
- Uncaught exceptions leaking internal details.
