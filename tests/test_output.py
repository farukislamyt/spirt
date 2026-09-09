from spirt.collection import CollectionResult, CollectionStatus
from spirt.models import SocialProfile
from spirt.output import render_result_json


def test_render_result_json_contains_status_and_profile() -> None:
    profile = SocialProfile(platform="facebook", profile_url="https://facebook.com/example")
    output = render_result_json(CollectionResult(CollectionStatus.SUCCESS, data=profile))

    assert '"status": "success"' in output
    assert '"platform": "facebook"' in output


def test_render_result_json_contains_error() -> None:
    output = render_result_json(CollectionResult(CollectionStatus.FAILED, error="parser failure"))

    assert '"status": "failed"' in output
    assert '"error": "parser failure"' in output
