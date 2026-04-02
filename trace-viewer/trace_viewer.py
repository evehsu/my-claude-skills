#!/usr/bin/env python3
"""
Trace Viewer — Visualize Claude Code session JSONL traces as interactive HTML.

Zero-dependency Python CLI. Produces a tabbed HTML file with:
  - Trace Tree: collapsible semantic conversation tree
  - Timeline: chronological flat view
  - Tool Usage: bar chart of tool call counts

Usage:
    python3 trace_viewer.py <input.jsonl> [-o output.html]
"""

import argparse
import json
import html as html_mod
import sys
from collections import Counter, defaultdict

TRUNCATE_LEN = 120
MAX_RAW_DISPLAY = 5000

COLORS = {
    "user_prompt": ("#e3f2fd", "#1976d2", "User"),
    "assistant_turn": ("#f3e5f5", "#7b1fa2", "Assistant"),
    "thinking": ("#fce4ec", "#c62828", "Thinking"),
    "text": ("#e8eaf6", "#3f51b5", "Text"),
    "tool_call": ("#fff3e0", "#e65100", "Tool Call"),
    "tool_result": ("#e8f5e9", "#2e7d32", "Tool Result"),
    "hook": ("#fffde7", "#f9a825", "Hook"),
    "agent_progress": ("#e0f7fa", "#00838f", "Agent Progress"),
    "system": ("#fafafa", "#9e9e9e", "System"),
    "snapshot": ("#eceff1", "#607d8b", "Snapshot"),
}

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def load_jsonl(path):
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def flatten_chain(records):
    nodes = {}
    children_map = defaultdict(list)
    root = None

    for r in records:
        uid = r.get("uuid")
        if not uid:
            uid = f"_syn_{id(r)}"
            r["uuid"] = uid
        nodes[uid] = r

    for uid, r in nodes.items():
        p = r.get("parentUuid")
        if p and p in nodes:
            children_map[p].append(uid)
        else:
            if root is None:
                root = uid

    for p in children_map:
        children_map[p].sort(key=lambda u: nodes[u].get("timestamp", ""))

    ordered = []
    def walk(uid):
        ordered.append(nodes[uid])
        for c in children_map.get(uid, []):
            walk(c)
    if root:
        walk(root)
    return ordered


def _join_user_content(content):
    if not content:
        return ""
    if all(isinstance(c, str) for c in content):
        return "".join(content)
    parts = []
    str_buf = []
    for c in content:
        if isinstance(c, str):
            str_buf.append(c)
        else:
            if str_buf:
                parts.append("".join(str_buf))
                str_buf = []
            parts.append(c)
    if str_buf:
        parts.append("".join(str_buf))
    return parts


def _tool_input_summary(name, inp):
    if not isinstance(inp, dict):
        return str(inp)[:TRUNCATE_LEN]
    if name in ("Read", "Write", "Edit"):
        return inp.get("file_path", "")
    if name == "Bash":
        desc = inp.get("description", "")
        cmd = inp.get("command", "")
        return desc if desc else cmd[:TRUNCATE_LEN]
    if name == "Grep":
        return f"{inp.get('pattern', '')} in {inp.get('path', '.')}"
    if name == "Glob":
        return inp.get("pattern", "")
    if name == "Agent":
        return inp.get("prompt", "")[:TRUNCATE_LEN]
    if name == "ToolSearch":
        return inp.get("query", "")
    if name == "ExitPlanMode":
        return inp.get("plan", "")[:TRUNCATE_LEN]
    for v in inp.values():
        if isinstance(v, str):
            return v[:TRUNCATE_LEN]
    return json.dumps(inp)[:TRUNCATE_LEN]


def _extract_tool_result_text(block):
    inner = block.get("content", "")
    if isinstance(inner, str):
        return inner
    if isinstance(inner, list):
        texts = []
        for ib in inner:
            if isinstance(ib, dict):
                t = ib.get("text", "")
                if t:
                    texts.append(t)
                elif ib.get("type") == "tool_reference":
                    texts.append("[tool_reference]")
                else:
                    texts.append(json.dumps(ib))
            else:
                texts.append(str(ib))
        return "\n".join(texts)
    return str(inner)


def build_semantic_tree(records):
    ordered = flatten_chain(records)
    turns = []
    tool_call_by_id = {}
    current_assistant_turn = None
    last_tool_calls = []

    for r in ordered:
        rtype = r.get("type")
        ts = r.get("timestamp", "")
        msg = r.get("message", {})
        content = msg.get("content", []) if isinstance(msg, dict) else []

        if rtype == "user":
            has_tool_result = any(
                isinstance(c, dict) and c.get("type") == "tool_result"
                for c in content
            )

            if has_tool_result:
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_result":
                        tool_use_id = c.get("tool_use_id", "")
                        result_text = _extract_tool_result_text(c)
                        result_node = {
                            "type": "tool_result",
                            "text": result_text,
                            "ts": ts,
                            "tool_use_id": tool_use_id,
                        }
                        if tool_use_id in tool_call_by_id:
                            tool_call_by_id[tool_use_id]["children"].append(result_node)
                        elif current_assistant_turn:
                            current_assistant_turn["children"].append(result_node)
            else:
                joined = _join_user_content(content)
                if isinstance(joined, str):
                    text = joined
                else:
                    text = " ".join(p if isinstance(p, str) else json.dumps(p) for p in joined)

                if not text.strip():
                    continue

                current_assistant_turn = None
                last_tool_calls = []

                is_meta = r.get("isMeta", False)
                turn = {
                    "type": "user_prompt",
                    "summary": text[:TRUNCATE_LEN].replace("\n", " "),
                    "raw": text,
                    "ts": ts,
                    "is_meta": is_meta,
                    "children": [],
                }
                turns.append(turn)

        elif rtype == "assistant":
            if current_assistant_turn is None:
                current_assistant_turn = {
                    "type": "assistant_turn",
                    "summary": "",
                    "ts": ts,
                    "children": [],
                }
                turns.append(current_assistant_turn)

            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type", "")

                if btype == "thinking":
                    text = block.get("text", "")
                    if text.strip():
                        current_assistant_turn["children"].append({
                            "type": "thinking",
                            "text": text,
                            "ts": ts,
                        })

                elif btype == "text":
                    text = block.get("text", "")
                    if text.strip():
                        current_assistant_turn["children"].append({
                            "type": "text",
                            "text": text,
                            "ts": ts,
                        })
                        if not current_assistant_turn["summary"]:
                            current_assistant_turn["summary"] = text[:TRUNCATE_LEN].replace("\n", " ")

                elif btype == "tool_use":
                    tool_name = block.get("name", "?")
                    tool_input = block.get("input", {})
                    tool_id = block.get("id", "")
                    tc_node = {
                        "type": "tool_call",
                        "name": tool_name,
                        "input": tool_input,
                        "input_summary": _tool_input_summary(tool_name, tool_input),
                        "tool_id": tool_id,
                        "ts": ts,
                        "children": [],
                    }
                    current_assistant_turn["children"].append(tc_node)
                    tool_call_by_id[tool_id] = tc_node
                    last_tool_calls.append(tc_node)

        elif rtype == "progress":
            data = r.get("data", {})
            subtype = data.get("type", "")

            if subtype == "hook_progress":
                hook_name = data.get("hookName", "hook")
                hook_node = {
                    "type": "hook",
                    "text": hook_name,
                    "ts": ts,
                    "raw": json.dumps(data, indent=2),
                }
                if last_tool_calls:
                    last_tool_calls[-1]["children"].append(hook_node)
                elif current_assistant_turn:
                    current_assistant_turn["children"].append(hook_node)
                else:
                    turns.append({
                        "type": "system",
                        "summary": hook_name,
                        "raw": json.dumps(data, indent=2),
                        "ts": ts,
                        "children": [],
                    })

            elif subtype == "agent_progress":
                content_text = data.get("content", "")
                if content_text and content_text.strip():
                    ap_node = {
                        "type": "agent_progress",
                        "text": content_text,
                        "ts": ts,
                    }
                    if last_tool_calls:
                        last_tool_calls[-1]["children"].append(ap_node)
                    elif current_assistant_turn:
                        current_assistant_turn["children"].append(ap_node)

        elif rtype == "file-history-snapshot":
            turns.append({
                "type": "snapshot",
                "summary": "File history snapshot",
                "raw": json.dumps(r.get("snapshot", {}), indent=2),
                "ts": ts,
                "children": [],
            })

    for turn in turns:
        if turn["type"] == "assistant_turn" and not turn.get("summary"):
            for child in turn.get("children", []):
                if child["type"] == "tool_call":
                    turn["summary"] = f"{child['name']}: {child['input_summary']}"
                    break
                elif child["type"] in ("text", "thinking"):
                    turn["summary"] = child["text"][:TRUNCATE_LEN].replace("\n", " ")
                    break
            if not turn.get("summary"):
                n_children = len(turn.get("children", []))
                turn["summary"] = f"({n_children} blocks)"

    return turns


def compute_stats(records):
    stats = {
        "total": len(records),
        "types": Counter(),
        "tools": Counter(),
        "thinking_chars": 0,
        "output_chars": 0,
        "timestamps": [],
    }
    for r in records:
        stats["types"][r.get("type", "unknown")] += 1
        ts = r.get("timestamp")
        if ts:
            stats["timestamps"].append(ts)
        msg = r.get("message", {})
        if isinstance(msg, dict):
            for block in msg.get("content", []):
                if isinstance(block, dict):
                    if block.get("type") == "tool_use":
                        stats["tools"][block.get("name", "?")] += 1
                    elif block.get("type") == "thinking":
                        stats["thinking_chars"] += len(block.get("text", ""))
                    elif block.get("type") == "text":
                        stats["output_chars"] += len(block.get("text", ""))
    if stats["timestamps"]:
        stats["time_range"] = (min(stats["timestamps"]), max(stats["timestamps"]))
    return stats


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _esc(text):
    return html_mod.escape(str(text)) if text else ""


def _ts_short(ts):
    if not ts:
        return ""
    if "T" in ts:
        return ts.split("T")[-1][:8]
    return ts[:8]


def _truncate_raw(text, max_len=MAX_RAW_DISPLAY):
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"\n\n... (truncated, {len(text):,} total chars)"


# ---------------------------------------------------------------------------
# Shared CSS (used once in the combined HTML <head>)
# ---------------------------------------------------------------------------

SHARED_CSS = """
.tv { font-family: 'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace; font-size: 13px; line-height: 1.5; }
.tv-stats { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 14px; }
.tv-stat { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 10px 14px; min-width: 120px; }
.tv-stat .label { font-size: 10px; color: #6c757d; text-transform: uppercase; letter-spacing: 0.5px; }
.tv-stat .value { font-size: 18px; font-weight: 600; color: #212529; }
.tv-ctrl { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; align-items: center; }
.tv-ctrl button { padding: 4px 10px; border: 1px solid #ccc; border-radius: 4px; background: #fff; cursor: pointer; font-size: 12px; }
.tv-ctrl button:hover { background: #e9ecef; }
.tv-ctrl label { font-size: 12px; margin-left: 10px; cursor: pointer; user-select: none; }

.tv-tree details { margin: 0; }
.tv-tree summary { cursor: pointer; list-style: none; padding: 3px 6px; border-radius: 4px; margin: 1px 0; display: flex; align-items: center; gap: 6px; }
.tv-tree summary::-webkit-details-marker { display: none; }
.tv-tree summary::before { content: '\\25B6'; font-size: 9px; transition: transform 0.15s; display: inline-block; width: 12px; flex-shrink: 0; color: #999; }
.tv-tree details[open] > summary::before { transform: rotate(90deg); }
.tv-tree summary:hover { background: #f5f5f5; }

.tv-badge { display: inline-block; padding: 1px 8px; border-radius: 3px; font-size: 11px; font-weight: 600; white-space: nowrap; flex-shrink: 0; }
.tv-sum { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; min-width: 0; }
.tv-meta { font-size: 11px; color: #999; white-space: nowrap; flex-shrink: 0; }
.tv-raw { background: #fafafa; border: 1px solid #eee; border-radius: 4px; padding: 8px 10px; margin: 2px 0 2px 30px; max-height: 400px; overflow: auto; white-space: pre-wrap; word-break: break-word; font-size: 12px; color: #333; }

.tv-d0 { margin-left: 0; }
.tv-d1 { margin-left: 20px; }
.tv-d2 { margin-left: 40px; }
.tv-d3 { margin-left: 56px; }

.tv-turn-user_prompt > summary { background: #e3f2fd; border-left: 4px solid #1976d2; }
.tv-turn-assistant_turn > summary { background: #f3e5f5; border-left: 4px solid #7b1fa2; }
.tv-turn-snapshot > summary { background: #eceff1; border-left: 4px solid #607d8b; opacity: 0.6; }
.tv-turn-system > summary { background: #fafafa; border-left: 4px solid #9e9e9e; opacity: 0.7; }

.tv-type-hook > summary { opacity: 0.5; }
.tv-type-hook:hover > summary { opacity: 0.8; }
.tv-type-agent_progress > summary { opacity: 0.6; }

.tv-hidden { display: none !important; }
.tv-bar { display: inline-block; height: 14px; background: #007bff; border-radius: 2px; margin-right: 6px; vertical-align: middle; }
.tv-tool-tbl { border-collapse: collapse; font-size: 12px; margin-top: 6px; }
.tv-tool-tbl td, .tv-tool-tbl th { border: 1px solid #dee2e6; padding: 3px 8px; }
.tv-tool-tbl th { background: #f8f9fa; text-align: left; }

/* Tab bar */
.tv-tabs { display: flex; gap: 0; border-bottom: 2px solid #dee2e6; margin-bottom: 16px; }
.tv-tab { padding: 8px 20px; cursor: pointer; font-size: 13px; font-weight: 600; border: 1px solid transparent; border-bottom: none; border-radius: 6px 6px 0 0; background: transparent; color: #666; }
.tv-tab:hover { background: #f8f9fa; }
.tv-tab.active { background: #fff; color: #212529; border-color: #dee2e6; margin-bottom: -2px; border-bottom: 2px solid #fff; }
.tv-panel { display: none; }
.tv-panel.active { display: block; }
"""


# ---------------------------------------------------------------------------
# View renderers (return HTML fragments, no <style> tags)
# ---------------------------------------------------------------------------

def render_trace_tree(turns, stats):
    parts = []

    # Stats banner
    tool_count = sum(stats["tools"].values())
    time_range = stats.get("time_range", ("", ""))
    parts.append('<div class="tv-stats">')
    for label, value in [
        ("Records", stats["total"]),
        ("Turns", len(turns)),
        ("Tool Calls", tool_count),
        ("Thinking", f"{stats['thinking_chars']:,}c"),
        ("Output", f"{stats['output_chars']:,}c"),
    ]:
        parts.append(f'<div class="tv-stat"><div class="label">{label}</div><div class="value">{value}</div></div>')
    parts.append('</div>')

    if stats["tools"]:
        parts.append('<details style="margin-bottom:10px"><summary style="cursor:pointer;font-size:12px;color:#666">Tool usage breakdown</summary>')
        parts.append('<table class="tv-tool-tbl"><tr><th>Tool</th><th>Count</th><th></th></tr>')
        max_c = max(stats["tools"].values())
        for name, count in stats["tools"].most_common():
            bar_w = max(2, int(200 * count / max_c))
            parts.append(f'<tr><td>{_esc(name)}</td><td>{count}</td><td><span class="tv-bar" style="width:{bar_w}px"></span></td></tr>')
        parts.append('</table></details>')

    if time_range[0]:
        parts.append(f'<div style="font-size:11px;color:#999;margin-bottom:10px">Session: {_esc(time_range[0])} &rarr; {_esc(time_range[1])}</div>')

    # Controls
    parts.append('<div class="tv-ctrl">')
    parts.append('<button onclick="tvExp(true)">Expand All</button>')
    parts.append('<button onclick="tvExp(false)">Collapse All</button>')
    parts.append('<button onclick="tvLevel(0)">Turns Only</button>')
    parts.append('<button onclick="tvLevel(1)">+ Blocks</button>')
    parts.append('<button onclick="tvLevel(2)">+ Tool I/O</button>')
    parts.append('<label><input type="checkbox" onchange="tvToggle(\'tv-type-hook\',this.checked); tvToggle(\'tv-type-agent_progress\',this.checked)"> Hide hooks/progress</label>')
    parts.append('<label><input type="checkbox" onchange="tvToggle(\'tv-type-thinking\',this.checked)"> Hide thinking</label>')
    parts.append('<label><input type="checkbox" onchange="tvToggle(\'tv-turn-snapshot\',this.checked)"> Hide snapshots</label>')
    parts.append('</div>')

    # Tree
    parts.append('<div class="tv-tree">')

    def render_node(node, depth):
        ntype = node["type"]
        ts = _ts_short(node.get("ts", ""))
        color = COLORS.get(ntype, ("#eee", "#ccc", ntype))
        badge_bg, border, label = color
        depth_cls = f"tv-d{min(depth, 3)}"
        type_cls = f"tv-type-{ntype}" if depth > 0 else f"tv-turn-{ntype}"
        children = node.get("children", [])

        if ntype == "user_prompt":
            summary = node.get("summary", "")
            meta = "meta" if node.get("is_meta") else ""
        elif ntype == "assistant_turn":
            summary = node.get("summary", "")
            n_tools = sum(1 for c in children if c["type"] == "tool_call")
            n_think = sum(1 for c in children if c["type"] == "thinking")
            meta_parts = []
            if n_think:
                meta_parts.append(f"{n_think} thinking")
            if n_tools:
                meta_parts.append(f"{n_tools} tool calls")
            meta = " | ".join(meta_parts)
        elif ntype == "tool_call":
            label = node.get("name", "Tool")
            badge_bg, border = "#fff3e0", "#e65100"
            summary = node.get("input_summary", "")
            n_results = sum(1 for c in children if c["type"] == "tool_result")
            meta = f"{n_results} result(s)" if n_results else ""
        elif ntype == "thinking":
            text = node.get("text", "")
            summary = text[:TRUNCATE_LEN].replace("\n", " ")
            meta = f"{len(text):,} chars"
        elif ntype == "text":
            summary = node.get("text", "")[:TRUNCATE_LEN].replace("\n", " ")
            meta = ""
        elif ntype == "tool_result":
            text = node.get("text", "")
            summary = text[:TRUNCATE_LEN].replace("\n", " ")
            meta = f"{len(text):,} chars"
        elif ntype == "hook":
            summary = node.get("text", "")
            meta = ""
        elif ntype == "agent_progress":
            summary = node.get("text", "")[:TRUNCATE_LEN].replace("\n", " ")
            meta = ""
        else:
            summary = node.get("summary", "")
            meta = ""

        if ntype == "tool_call":
            raw = json.dumps(node.get("input", {}), indent=2)
        elif ntype in ("thinking", "text", "tool_result", "agent_progress"):
            raw = node.get("text", "")
        elif ntype == "user_prompt":
            raw = node.get("raw", "")
        elif ntype == "hook":
            raw = node.get("raw", node.get("text", ""))
        else:
            raw = node.get("raw", "")

        raw_display = _truncate_raw(raw)

        parts.append(
            f'<details class="{depth_cls} {type_cls}" data-depth="{depth}">'
            f'<summary style="border-left:3px solid {border}">'
            f'<span class="tv-badge" style="background:{badge_bg}">{_esc(label)}</span>'
            f'<span class="tv-sum">{_esc(summary)}</span>'
        )
        if meta:
            parts.append(f'<span class="tv-meta">{_esc(meta)}</span>')
        if ts:
            parts.append(f'<span class="tv-meta">{_esc(ts)}</span>')
        parts.append('</summary>')

        if raw_display.strip():
            parts.append(f'<pre class="tv-raw">{_esc(raw_display)}</pre>')

        for child in children:
            render_node(child, depth + 1)

        parts.append('</details>')

    for turn in turns:
        render_node(turn, 0)

    parts.append('</div>')
    return "\n".join(parts)


def render_timeline(turns):
    parts = []
    parts.append('<h3 style="margin:8px 0">Chronological Timeline</h3>')
    parts.append('<div style="max-height:600px;overflow:auto">')

    for turn in turns:
        ttype = turn["type"]
        ts = _ts_short(turn.get("ts", ""))
        color = COLORS.get(ttype, ("#eee", "#ccc", ttype))
        badge_bg, border, label = color

        if ttype == "snapshot":
            continue

        if ttype == "user_prompt":
            summary = turn.get("summary", "")
            if turn.get("is_meta"):
                label = "System"
                badge_bg = "#fafafa"
            parts.append(
                f'<div style="display:flex;gap:8px;align-items:center;padding:4px 6px;border-bottom:1px solid #f0f0f0">'
                f'<span style="font-size:11px;color:#888;width:55px;flex-shrink:0">{ts}</span>'
                f'<span class="tv-badge" style="background:{badge_bg}">{label}</span>'
                f'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{_esc(summary[:150])}</span>'
                f'</div>'
            )

        elif ttype == "assistant_turn":
            summary = turn.get("summary", "")
            n_tools = sum(1 for c in turn.get("children", []) if c["type"] == "tool_call")
            extra = f" [{n_tools} tool calls]" if n_tools else ""
            parts.append(
                f'<div style="display:flex;gap:8px;align-items:center;padding:4px 6px;border-bottom:1px solid #f0f0f0">'
                f'<span style="font-size:11px;color:#888;width:55px;flex-shrink:0">{ts}</span>'
                f'<span class="tv-badge" style="background:{badge_bg}">{label}</span>'
                f'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{_esc(summary[:120])}{_esc(extra)}</span>'
                f'</div>'
            )

            for child in turn.get("children", []):
                if child["type"] == "tool_call":
                    tc_ts = _ts_short(child.get("ts", ""))
                    tc_name = child.get("name", "")
                    tc_summary = child.get("input_summary", "")
                    result_preview = ""
                    for gc in child.get("children", []):
                        if gc["type"] == "tool_result":
                            result_preview = gc.get("text", "")[:80].replace("\n", " ")
                            break
                    parts.append(
                        f'<div style="display:flex;gap:8px;align-items:center;padding:2px 6px 2px 30px;border-bottom:1px solid #f8f8f8;font-size:12px">'
                        f'<span style="font-size:11px;color:#888;width:55px;flex-shrink:0">{tc_ts}</span>'
                        f'<span class="tv-badge" style="background:#fff3e0;font-size:10px">{_esc(tc_name)}</span>'
                        f'<span style="color:#555;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{_esc(tc_summary[:80])}'
                    )
                    if result_preview:
                        parts.append(f' <span style="color:#2e7d32">&rarr; {_esc(result_preview)}</span>')
                    parts.append('</span></div>')

        elif ttype == "system":
            parts.append(
                f'<div style="display:flex;gap:8px;align-items:center;padding:4px 6px;border-bottom:1px solid #f0f0f0;opacity:0.7">'
                f'<span style="font-size:11px;color:#888;width:55px;flex-shrink:0">{ts}</span>'
                f'<span class="tv-badge" style="background:#fafafa">{label}</span>'
                f'<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{_esc(turn.get("summary", "")[:100])}</span>'
                f'</div>'
            )

    parts.append('</div>')
    return "\n".join(parts)


def render_tool_chart(stats):
    if not stats["tools"]:
        return "<p>No tool calls found.</p>"

    parts = []
    parts.append('<h3 style="margin:8px 0">Tool Usage</h3>')
    max_count = max(stats["tools"].values())

    for name, count in stats["tools"].most_common():
        bar_w = max(4, int(300 * count / max_count))
        parts.append(
            f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0">'
            f'<span style="width:120px;text-align:right;font-size:12px">{_esc(name)}</span>'
            f'<span class="tv-bar" style="width:{bar_w}px"></span>'
            f'<span style="font-size:12px;color:#666">{count}</span>'
            f'</div>'
        )

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Combined HTML document with tabs
# ---------------------------------------------------------------------------

def render_combined_html(turns, stats, title="Trace Viewer"):
    trace_tree = render_trace_tree(turns, stats)
    timeline = render_timeline(turns)
    tool_chart = render_tool_chart(stats)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<style>
body {{ margin: 0; padding: 20px; background: #fff; }}
{SHARED_CSS}
</style>
</head>
<body>
<div class="tv" id="tv-root">

<div class="tv-tabs">
  <div class="tv-tab active" onclick="tvSwitchTab('trace-tree', this)">Trace Tree</div>
  <div class="tv-tab" onclick="tvSwitchTab('timeline', this)">Timeline</div>
  <div class="tv-tab" onclick="tvSwitchTab('tool-usage', this)">Tool Usage</div>
</div>

<div id="panel-trace-tree" class="tv-panel active">
{trace_tree}
</div>

<div id="panel-timeline" class="tv-panel">
{timeline}
</div>

<div id="panel-tool-usage" class="tv-panel">
{tool_chart}
</div>

</div>

<script>
(function() {{
    const root = document.getElementById('tv-root');
    const tree = root.querySelector('.tv-tree');

    window.tvSwitchTab = function(id, tabEl) {{
        root.querySelectorAll('.tv-panel').forEach(p => p.classList.remove('active'));
        root.querySelectorAll('.tv-tab').forEach(t => t.classList.remove('active'));
        document.getElementById('panel-' + id).classList.add('active');
        tabEl.classList.add('active');
    }};

    window.tvExp = function(open) {{
        if (!tree) return;
        tree.querySelectorAll('details').forEach(d => d.open = open);
    }};

    window.tvLevel = function(maxDepth) {{
        if (!tree) return;
        tree.querySelectorAll('details').forEach(d => {{
            const depth = parseInt(d.getAttribute('data-depth') || '0');
            d.open = depth <= maxDepth;
        }});
    }};

    window.tvToggle = function(cls, hide) {{
        if (!tree) return;
        tree.querySelectorAll('.' + cls).forEach(el => {{
            el.classList.toggle('tv-hidden', hide);
        }});
    }};
}})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Visualize Claude Code session JSONL traces as interactive HTML."
    )
    parser.add_argument("input", help="Path to the trace JSONL file")
    parser.add_argument("-o", "--output", help="Output HTML path (default: same basename with .html)")
    args = parser.parse_args()

    import os
    input_path = args.input
    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(input_path)[0]
        output_path = base + ".html"

    records = load_jsonl(input_path)
    turns = build_semantic_tree(records)
    stats = compute_stats(records)

    title = os.path.basename(input_path)
    html = render_combined_html(turns, stats, title=title)

    with open(output_path, "w") as f:
        f.write(html)

    tool_count = sum(stats["tools"].values())
    print(f"Records:    {stats['total']}")
    print(f"Turns:      {len(turns)}")
    print(f"Tool calls: {tool_count} ({', '.join(f'{n}:{c}' for n, c in stats['tools'].most_common())})")
    print(f"Output:     {output_path}")


if __name__ == "__main__":
    main()
