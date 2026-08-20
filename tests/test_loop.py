def test_four_names_import_from_the_package():
    from scratch_agent.loop import reason, pending, decide, loop

    assert callable(reason)
    assert callable(pending)
    assert callable(decide)
    assert callable(loop)
