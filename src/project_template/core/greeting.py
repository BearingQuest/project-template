from project_template.errors import InputError


def greet(name: str, max_length: int) -> str:
    """Return a greeting for name, which must be 1 to max_length printable characters."""
    cleaned = name.strip()
    if not cleaned:
        raise InputError("name must not be empty")
    if len(cleaned) > max_length:
        raise InputError(f"name must be at most {max_length} characters")
    if not cleaned.isprintable():
        raise InputError("name must contain only printable characters")
    return f"Hello, {cleaned}!"
