def escape_markdown_currency(
    text: str,
) -> str:
    return text.replace("$", r"\$")
