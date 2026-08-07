from uuid import uuid4

from atlas.agent.state import AtlasState, RoutePlan


def test_state_requires_typed_route_and_version_metadata() -> None:
    state = AtlasState(
        thread_id=uuid4(),
        request_id=uuid4(),
        request="How does LangGraph route state?",
        language="en-US",
        route=RoutePlan(intent="factual", subquestions=["How does LangGraph route state?"]),
    )
    assert state.route.intent == "factual"
    assert state.state_version == 1
    assert state.node_history == []
