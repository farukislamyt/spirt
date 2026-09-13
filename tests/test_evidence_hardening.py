import pytest

from spirt.evidence import Evidence


@pytest.mark.parametrize("source_url", ["", "example.com", "ftp://example.com/path", "https:///missing-host"])
def test_evidence_rejects_invalid_source_url(source_url: str) -> None:
    with pytest.raises(ValueError, match="source_url"):
        Evidence("display_name", "Example", source_url)


@pytest.mark.parametrize("field", ["", "   "])
def test_evidence_rejects_empty_field(field: str) -> None:
    with pytest.raises(ValueError, match="field"):
        Evidence(field, "Example", "https://example.com/profile")


@pytest.mark.parametrize("method", ["", "   "])
def test_evidence_rejects_empty_method(method: str) -> None:
    with pytest.raises(ValueError, match="method"):
        Evidence("display_name", "Example", "https://example.com/profile", method=method)
