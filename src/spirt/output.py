from __future__ import annotations

import json

from spirt.models import SocialProfile


def render_json(profile: SocialProfile) -> str:
    """Render a profile as stable, human-readable JSON."""
    return json.dumps(profile.to_dict(), indent=2, ensure_ascii=False)
