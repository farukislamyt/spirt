from spirt.normalizers import normalize_profile


def test_normalize_profile_prefers_canonical_metadata() -> None:
    profile = normalize_profile(
        platform="facebook",
        profile_url="https://facebook.com/example",
        metadata={
            "open_graph": {
                "og:title": "Example User",
                "og:url": "https://www.facebook.com/example",
                "og:description": "Public bio",
                "og:see_also": "https://example.com",
                "og:image": "https://example.com/avatar.jpg",
            },
            "collection_status": "success",
        },
    )

    assert profile.profile_url == "https://www.facebook.com/example"
    assert profile.username == "example"
    assert profile.display_name == "Example User"
    assert profile.bio == "Public bio"
    assert profile.website == "https://example.com"
    assert len(profile.evidence) == 4
    assert profile.metadata["normalization"]["version"] == 1


def test_normalize_profile_falls_back_to_json_ld() -> None:
    profile = normalize_profile(
        platform="example",
        profile_url="https://example.com/person",
        metadata={"open_graph": {}},
        json_ld=[{"@type": "Person", "name": "JSON Person"}],
    )

    assert profile.display_name == "JSON Person"
    assert profile.username == "person"
