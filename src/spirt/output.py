from __future__ import annotations

import json

from spirt.collection import CollectionResult
from spirt.models import SocialProfile


def render_json(profile: SocialProfile) -> str:
    """Render a profile as stable, human-readable JSON."""
    return json.dumps(profile.to_dict(), indent=2, ensure_ascii=False)


def render_result_json(result: CollectionResult) -> str:
    """Render a complete collection result as stable JSON."""
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
