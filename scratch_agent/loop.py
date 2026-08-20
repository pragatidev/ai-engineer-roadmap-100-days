"""Three hops and the loop that holds them. Plain Python. No LangChain."""


def reason(question):
    """Hop 1. The model looks at the question."""
    return {"hop": 1, "name": "reason", "question": question}


def pending():
    """Hop 2. Tool slot. Arguments stay empty in this stub."""
    return {"hop": 2, "name": "pending", "arguments": {}}


def decide(question, seen):
    """Hop 3. The model looks at the question and at what the tool already returned."""
    return {"hop": 3, "name": "decide", "question": question, "seen": seen}


def loop(question):
    """Run reason, pending, then decide, in that order."""
    first = reason(question)
    tool_slot = pending()
    second = decide(question, seen=tool_slot)
    return [first, tool_slot, second]
