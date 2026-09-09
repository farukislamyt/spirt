import pytest

from spirt.evidence import Evidence


def test_evidence_serializes_provenance() -> None:
    evidence = Evidence(
        field="display_name",
        value="Example User",
        source_url="https://www.facebook.com/example",
        method="open_graph",
        confidence=0.95,
    )
    assert evidence.to_dict() == {
        "field": "display_name",
        "value": "Example User",
        "source_url": "https://www.facebook.com/example",
        "source_type": "public_webpage",
        "method": "open_graph",
        "confidence": 0.95,
    }


def test_evidence_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        Evidence("bio", "text", "https://example.com", confidence=1.1)
