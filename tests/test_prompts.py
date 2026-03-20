import pytest

from voicetools.prompts import PromptBuilder, build_system_prompt


def test_build_system_prompt_contains_valet():
    result = build_system_prompt()
    assert "Valet" in result


def test_build_system_prompt_contains_default_shops():
    result = build_system_prompt()
    assert "Elite Detail Studio" in result
    assert "Diamond Wash" in result


def test_build_system_prompt_with_shops_list():
    shops = [
        {"name": "Test Shop", "location": "District 1", "rating": 4.5, "specialty": "Wash only"}
    ]
    result = build_system_prompt(shops=shops)
    assert "Test Shop" in result
    assert "District 1" in result


def test_prompt_builder_raises_on_missing_vars():
    builder = PromptBuilder("{foo} and {bar}", required_vars={"foo", "bar"})
    with pytest.raises(ValueError, match="Missing required template vars"):
        builder.build(foo="hello")


def test_prompt_builder_substitutes_vars():
    builder = PromptBuilder("Hello {name}!", required_vars={"name"})
    result = builder.build(name="World")
    assert result == "Hello World!"
