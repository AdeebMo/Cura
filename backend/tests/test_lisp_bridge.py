from app.integrations.lisp_bridge import LispBridge


def test_lisp_bridge_normalizes_common_symptoms() -> None:
    bridge = LispBridge()
    result = bridge.normalize("I have a high fever and I am coughing a lot.")

    assert "fever" in result.canonical_symptoms
    assert "cough" in result.canonical_symptoms
    assert any(match.source == "high fever" for match in result.matched_phrases)


def test_lisp_bridge_normalizes_multiword_phase_four_symptoms() -> None:
    bridge = LispBridge()
    result = bridge.normalize("I have loss of taste and smell, a dry mouth, and dizziness.")

    assert "loss_of_taste_smell" in result.canonical_symptoms
    assert "dry_mouth" in result.canonical_symptoms
    assert "dizziness" in result.canonical_symptoms
    assert result.unknown_terms == []
    assert any(match.source == "loss of taste and smell" for match in result.matched_phrases)
