import pytest

from atlas.reports.planner import plan_report
from atlas.reports.schemas import ReportLocale, ReportSpec

from .test_planner import Source, _completed


@pytest.mark.asyncio
async def test_locales_share_citation_identity_and_localize_presentation() -> None:
    source = _completed()
    english = await plan_report(
        ReportSpec(
            source_run_id=source.run_id,
            audience="engineer",
            scope="comparison",
            locale=ReportLocale.EN_US,
        ),
        owner_key_hash="visitor",
        source=Source(source),
    )
    spanish = await plan_report(
        ReportSpec(
            source_run_id=source.run_id,
            audience="engineer",
            scope="comparison",
            locale=ReportLocale.ES_MX,
        ),
        owner_key_hash="visitor",
        source=Source(source),
    )
    english_manifest = [
        (item.citation_id, item.evidence_id, item.url, item.excerpt)
        for item in english.citations
    ]
    spanish_manifest = [
        (item.citation_id, item.evidence_id, item.url, item.excerpt) for item in spanish.citations
    ]
    assert english_manifest == spanish_manifest
    assert english.sections[0].title != spanish.sections[0].title
    assert english.sections[0].narrative != spanish.sections[0].narrative
