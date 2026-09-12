import pytest

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


def test_success_requires_data() -> None:
    with pytest.raises(ValueError, match="data"):
        CollectionResult(CollectionStatus.SUCCESS)


@pytest.mark.parametrize("status", [CollectionStatus.UNAVAILABLE, CollectionStatus.FAILED])
def test_unsuccessful_terminal_status_requires_error(status: CollectionStatus) -> None:
    with pytest.raises(ValueError, match="error"):
        CollectionResult(status)


def test_invalid_status_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="CollectionStatus"):
        CollectionResult("success")  # type: ignore[arg-type]
