"""Tests that every registered MCP tool carries explicit annotations."""

import pytest

from server.main import create_server

DESTRUCTIVE_TOOLS = {
    "add_user_ratings",
    "clear_auth",
    "remove_from_history",
    "remove_playback_item",
    "remove_user_ratings",
    "remove_user_watchlist",
}


@pytest.mark.asyncio
async def test_every_tool_declares_read_only_hint() -> None:
    """New tools must state whether they only read, so clients can trust it."""
    tools = await create_server().list_tools()

    assert tools, "expected the server to register tools"
    missing = [
        tool.name
        for tool in tools
        if tool.annotations is None or tool.annotations.readOnlyHint is None
    ]
    assert not missing, f"tools without an explicit readOnlyHint: {missing}"


@pytest.mark.asyncio
async def test_write_tools_declare_destructive_hint() -> None:
    """Tools that change state must say whether the change is destructive."""
    tools = await create_server().list_tools()

    for tool in tools:
        assert tool.annotations is not None
        if tool.annotations.readOnlyHint:
            continue
        assert tool.annotations.destructiveHint == (tool.name in DESTRUCTIVE_TOOLS), (
            f"unexpected destructiveHint on {tool.name}"
        )


@pytest.mark.asyncio
async def test_fetch_and_search_tools_are_read_only() -> None:
    """Lookup tools never write, everything else does."""
    tools = await create_server().list_tools()

    for tool in tools:
        assert tool.annotations is not None
        expected = tool.name.startswith(("fetch_", "search_"))
        assert tool.annotations.readOnlyHint is expected, tool.name
