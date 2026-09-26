# T12: MCP server and demo GIF

**Phase:** 3 Agent · **Estimate:** 2 h · **Depends on:** T09, T10, T20

## Ask

Expose `search_rules`, `query_delays` and `classify_incident` as an MCP server usable from Claude
Desktop or Claude Code, and record a demo GIF.

## Why

"Done when" requires it. MCP makes the tools usable from any MCP client, not only my agent.

## How

- Python MCP SDK, stdio transport, tool schemas with clear descriptions.
- `classify_incident` starts with the T20 prompt-based classifier; swap in the winner after T22.
- Config snippet for Claude Code / Claude Desktop in the README.

## Plan

- [ ] Server with three tools
- [ ] Local test with the MCP inspector
- [ ] Connect from Claude Code or Claude Desktop
- [ ] Record the demo GIF

## Acceptance criteria

- [ ] All three tools are listed and callable from an MCP client
- [ ] Setup instructions work from a clean clone
- [ ] Demo GIF is in `reports/figures/` and embedded in the README
