from spirt.correlation import correlate
from spirt.models import SocialProfile


def test_correlation_requires_explicit_signals() -> None:
    left = SocialProfile(platform="a", profile_url="https://a.example/alice", username="alice", display_name="Alice")
    right = SocialProfile(platform="b", profile_url="https://b.example/alice", username="alice", display_name="Alice")
    matches = correlate([left, right])
    assert len(matches) == 1
    assert matches[0].score == 0.8
    assert "same_username" in matches[0].reasons
