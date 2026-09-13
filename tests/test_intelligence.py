import pytest

from spirt.intelligence import build_evidence_graph, entity_resolution, resolve_target
from spirt.models import SocialProfile


def test_resolve_target_normalizes_username_without_network_access() -> None:
    result = resolve_target("@Alice", templates=("https://example.com/{username}", "https://social.example/{username}"))
    assert result.normalized == "alice"
    assert result.candidates == ("https://example.com/Alice", "https://social.example/Alice")


def test_resolve_target_rejects_unsafe_url() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        resolve_target("http://example.com/alice")


def test_entity_resolution_requires_threshold() -> None:
    left = SocialProfile(platform="a", profile_url="https://a.example/alice", username="alice", display_name="Alice")
    right = SocialProfile(platform="b", profile_url="https://b.example/alice", username="alice", display_name="Alice")
    matches = entity_resolution([left, right])
    assert len(matches) == 1
    assert matches[0].score == pytest.approx(0.8)
    assert matches[0].reasons == ("same_username", "same_display_name")


def test_entity_resolution_rejects_invalid_threshold() -> None:
    with pytest.raises(ValueError, match="threshold"):
        entity_resolution([], threshold=1.1)


def test_evidence_graph_materializes_explicit_signals() -> None:
    left = SocialProfile(platform="a", profile_url="https://a.example/alice", username="alice", website="https://example.org")
    right = SocialProfile(platform="b", profile_url="https://b.example/alice", username="alice", website="https://example.org")
    edges = build_evidence_graph([left, right])
    assert {edge.signal for edge in edges} == {"same_username", "same_website"}
    assert sum(edge.weight for edge in edges) == pytest.approx(0.9)
