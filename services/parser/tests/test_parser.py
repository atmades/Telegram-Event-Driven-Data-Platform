from app.parser import parse_expense_text, build_parsed_event


def test_parse_expense_text_valid():
    result = parse_expense_text("кофе 3500")

    assert result == {
        "description": "кофе",
        "amount": 3500.0,
        "currency": "ARS",
    }


def test_parse_expense_text_with_spaces_in_amount():
    result = parse_expense_text("ужин 1 200")

    assert result == {
        "description": "ужин",
        "amount": 1200.0,
        "currency": "ARS",
    }


def test_parse_expense_text_invalid_without_amount():
    result = parse_expense_text("просто текст")

    assert result is None


def test_build_parsed_event_valid():
    raw_event = {
        "event_id": "raw-123",
        "telegram": {
            "chat_id": 1,
            "user_id": 2,
            "username": "max",
            "text": "кофе 3500",
        },
    }

    event = build_parsed_event(raw_event)

    assert event is not None
    assert event.event_type == "expense_recorded"
    assert event.source == "parser"
    assert event.raw_event_id == "raw-123"
    assert event.expense.description == "кофе"
    assert event.expense.amount == 3500.0
    assert event.expense.currency == "ARS"
    assert event.telegram.username == "max"


def test_build_parsed_event_invalid_text():
    raw_event = {
        "event_id": "raw-123",
        "telegram": {
            "text": "просто текст",
        },
    }

    event = build_parsed_event(raw_event)

    assert event is None