<!--
<ai_agent_documentation>
  <file_meta>
    <name>ERROR_HANDLING.md</name>
    <version>1.0.0</version>
    <type>error_handling_guide</type>
    <purpose>Standard error handling patterns for API routes</purpose>
    <last_updated>2026-02-07</last_updated>
  </file_meta>
</ai_agent_documentation>
-->

# Error Handling Patterns

## API Validation
- Validate inputs early and return `400` with actionable messages.
- Use shared helpers in `aruco_generator/core/utils.py` where possible.

## Server Errors
- Wrap API handlers with `handle_api_errors` to standardize `500` responses.
- Log stack traces on server, return user-safe messages to clients.

## Database Optionality
- Treat DB persistence as optional. Guard writes with `current_app.config["USE_DB"]`.
- If DB is disabled, return success with a message indicating metrics were not persisted.

## Anti-patterns
- Generic “check your parameters” messages without context.
- Uncaught exceptions leaking internal details.
