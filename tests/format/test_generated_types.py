"""The component's types generated from the format's source (tools/build_format.py)."""

import re

import pytest

import build_format


@pytest.mark.feature("FORMAT-02")
def test_the_types_name_each_class_once_and_keep_the_links_pair():
    """DEF-001: json-schema-to-typescript named a type twice (Status1 for Status, Name1 for a field) and read the
    links' pair of keys as [unknown, unknown]."""
    types = build_format.types_text(build_format.schema_text())
    assert re.findall(r"\b[A-Z][A-Za-z]*\d\b", types) == []
    assert "unknown" not in types
    assert "links?: [string, string][];" in types
    assert types.count('export type Status = "SOUND" | "TO_LOOK_AT" | "BLOCKING" | "NOT_BUILT";') == 1
