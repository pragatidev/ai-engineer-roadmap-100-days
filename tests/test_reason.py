def test_legal_json_becomes_action():
    from scratch_agent.actions import Action, CallTool, Stop
    from scratch_agent.reason import action_from_model_text

    call = action_from_model_text(
        '{"kind": "call_tool", "name": "multiply", "arguments": {"a": 347, "b": 19}}'
    )
    stop = action_from_model_text('{"kind": "stop", "answer": "6593"}')
    assert call == CallTool(name="multiply", arguments={"a": 347, "b": 19})
    assert stop == Stop(answer="6593")
    assert isinstance(call, Action)
    assert isinstance(stop, Action)


def test_english_is_not_an_action():
    import json

    import pytest
    from scratch_agent.reason import action_from_model_text

    with pytest.raises(json.JSONDecodeError):
        action_from_model_text("Sure, I will multiply those, the answer is 6593.")
    with pytest.raises(json.JSONDecodeError):
        action_from_model_text("I will multiply, but first let me think.")
    with pytest.raises(ValueError):
        action_from_model_text(
            '{"kind": "maybe_multiply", "name": "multiply", "arguments": {"a": 347, "b": 19}}'
        )
