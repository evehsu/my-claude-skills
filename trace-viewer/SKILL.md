---
name: trace-viewer
description: Visualize AI agent trace JSONL files as interactive HTML with trace tree, timeline, and tool usage chart.
argument-hint: "<path-to-trace.jsonl>"
allowed-tools: Read, Bash, Glob, AskUserQuestion
---

# Trace Viewer

Converts Claude Code session JSONL trace files into interactive HTML visualizations with three tabbed views: a collapsible trace tree, a chronological timeline, and a tool usage bar chart.

## Workflow

1. **Find the JSONL file**
   - If an argument is provided, use it as the path.
   - Otherwise, use `Glob("**/*.jsonl")` to find candidates and ask the user to pick one.

2. **Verify it's a trace file**
   - Read the first few lines and confirm records contain `uuid` and `type` fields (expected for Claude Code session traces).
   - If the file doesn't look like a trace, inform the user and stop.

3. **Determine output path**
   - Default: same directory and basename as the input, with `.html` extension.
   - Example: `session.jsonl` → `session.html`

4. **Generate the HTML**
   ```bash
   python3 ~/.claude/skills/trace-viewer/trace_viewer.py "<input.jsonl>"
   ```
   - The script accepts an optional `-o <output.html>` flag to override the output path.

5. **Report results**
   - Show the stats printed by the script (records, turns, tool calls).
   - Provide the output file path.
   - Offer to open it: `open "<output.html>"`
