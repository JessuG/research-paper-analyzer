from app.analysis import PaperAnalysisService


def test_fallback_analysis_returns_expected_sections():
    service = PaperAnalysisService()

    result = service._fallback_analysis(
        abstract=(
            "This study evaluates a transformer-based model on a benchmark dataset. "
            "It compares baseline systems and reports improved classification accuracy."
        ),
        conclusion=(
            "The approach improves performance, but generalization across domains remains limited. "
            "Future work should test more diverse datasets."
        ),
    )

    assert set(result.keys()) == {"methodology", "findings", "research_gaps"}
    assert "Abstract length" in result["methodology"]
    assert "This study evaluates a transformer-based model on a benchmark dataset" in result["findings"]
    assert "Research gaps could not be fully inferred without live model analysis." in result["research_gaps"]
