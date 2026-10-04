from app.ui.formatting import (
    escape_markdown_currency,
)


def test_escape_markdown_currency_escapes_dollar_signs() -> None:
    text = "Revenue decreased by $497,649.98 and Computing declined by $451,913.17."

    result = escape_markdown_currency(text)

    assert result == (
        "Revenue decreased by \\$497,649.98 and Computing declined by \\$451,913.17."
    )


def test_escape_markdown_currency_preserves_text_without_currency() -> None:
    text = "Revenue decreased by 28.06%."

    result = escape_markdown_currency(text)

    assert result == text


def test_escape_markdown_currency_preserves_empty_string() -> None:
    assert escape_markdown_currency("") == ""
