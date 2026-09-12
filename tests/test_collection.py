import pytest

from spirt.collection import CollectionErrorCode, CollectionResult, CollectionStatus
from spirt.models import SocialProfile


def test_collection_status_values() -> None:
    assert CollectionStatus.SUCCESS.value == "success"
    assert CollectionStatus.PARTIAL.value == "partial"
    assert CollectionStatus.UNAVAILABLE.value == "unavailable"
    assert CollectionStatus.FAILED.value == "failed"


def test_collection_error_codes_are_stable() -> None:
    assert CollectionErrorCode.UNSUPPORTED_URL.value == "unsupported_url"
    assert CollectionErrorCode.NETWORK_UNAVAILABLE.value == "network_unavailable"
    assert CollectionErrorCode.INVALID_RESPONSE.value == "invalid_response"
    assert CollectionErrorCode.PARSE_ERROR.value == "parse_error"
    assert CollectionErrorCode.UNKNOWN.value == "unknown"


def test_collection_result_serializes_profile() -> None:
    profile = SocialProfile(platform="facebook", profile_url="https://facebook.com/example")
    result = CollectionResult(CollectionStatus.SUCCESS, data=profile)

    assert result.to_dict() == {
        "status": "success",
        "data": profile.to_dict(),
        "error": None,
        "error_code": None,
    }


def test_collection_result_serializes_error() -> None:
    result = CollectionResult(
        CollectionStatus.UNAVAILABLE,
        error="network failure",
        error_code=CollectionErrorCode.NETWORK_UNAVAILABLE,
    )

    assert result.to_dict() == {
        "status": "unavailable",
        "data": None,
        "error": "network failure",
        "error_code": "network_unavailable",
    }


def test_success_requires_data() -> None:
    with pytest.raises(ValueError, match="data"):
        CollectionResult(CollectionStatus.SUCCESS)


def test_success_cannot_contain_error() -> None:
    profile = SocialProfile(platform="facebook", profile_url="https://facebook.com/example")
    with pytest.raises(ValueError, match="cannot contain an error"):
        CollectionResult(
            CollectionStatus.SUCCESS,
            data=profile,
            error="unexpected",
            error_code=CollectionErrorCode.UNKNOWN,
        )


@pytest.mark.parametrize("status", [CollectionStatus.UNAVAILABLE, CollectionStatus.FAILED])
def test_unsuccessful_terminal_status_requires_error(status: CollectionStatus) -> None:
    with pytest.raises(ValueError, match="error"):
        CollectionResult(status)


def test_unsuccessful_terminal_status_requires_error_code() -> None:
    with pytest.raises(ValueError, match="error_code"):
        CollectionResult(CollectionStatus.FAILED, error="parse failure")


def test_partial_requires_data_or_error() -> None:
    with pytest.raises(ValueError, match="data or an error"):
        CollectionResult(CollectionStatus.PARTIAL)


def test_partial_error_requires_code() -> None:
    profile = SocialProfile(platform="facebook", profile_url="https://facebook.com/example")
    with pytest.raises(ValueError, match="error_code"):
        CollectionResult(CollectionStatus.PARTIAL, data=profile, error="partial failure")


def test_invalid_status_type_is_rejected() -> None:
    with pytest.raises(TypeError, match="CollectionStatus"):
        CollectionResult("success")  # type: ignore[arg-type]
