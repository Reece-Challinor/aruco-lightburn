"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>rate_limit.py</name>
    <type>shared_extension</type>
    <purpose>Shared Flask-Limiter instance; import and decorate expensive endpoints</purpose>
  </file_meta>
</ai_agent_documentation>
-->

Shared rate limiter.

Memory storage is intentional: on Vercel each function instance gets its own
counters (good enough for a free demo; escalate to Vercel WAF rules if abused),
and for Docker self-hosting limits apply per worker. Disabled in tests via
``RATELIMIT_ENABLED = False``.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=[],
    headers_enabled=True,
)
