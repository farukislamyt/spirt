from spirt.collection import CollectionResult, CollectionStatus
from spirt.models import SocialProfile


def test_collection_status_values() -> None:
    assert CollectionStatus.SUCCESS.value == "success"
    assert CollectionStatus.PARTIAL.value == "partial"
    assert CollectionStatus.UNAVAILABLE.value == "unavailable"
    assert CollectionStatus.FAILED.value == "failed"


def test_collection_result_serializes_profile() -> None:
    profile = SocialProfile(platform="facebook", profile_url="https://facebook.com/example")
    result = CollectionResult(CollectionStatus.SUCCESS, data=profile)

    assert result.to_dict() == {
        "status": "success",
        "data": profile.to_dict(),
        "error": None,
    }


def test_collection_result_serializes_error() -> None:
    result = CollectionResult(CollectionStatus.UNAVAILABLE, error="network failure")

    assert result.to_dict() == {
        "status": "unavailable",
        "data": None,
        "error": "network failure",
    }
