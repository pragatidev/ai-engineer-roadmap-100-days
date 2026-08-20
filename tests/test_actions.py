def test_call_tool_and_stop_construct():
    from scratch_agent.actions import Action, CallTool, Stop

    call = CallTool(name="multiply", arguments={"a": 347, "b": 19})
    stop = Stop(answer="6593")
    assert call.name == "multiply"
    assert call.arguments == {"a": 347, "b": 19}
    assert stop.answer == "6593"
    assert isinstance(call, Action)
    assert isinstance(stop, Action)
