"""
Sankey diagram renderer (flagship chart type).

Takes a spec of nodes + links and produces a polished, interactive Plotly
Sankey. The design choices here are what separate this from a default Plotly
Sankey:

  * Links inherit a translucent tint of their *source* node color, so flows
    read as "coming from" a node — this is the single biggest readability win.
  * Node labels can carry their throughput value inline, so the graphic is
    self-explanatory without hover.
  * Color is assigned automatically and distinctly; the caller never has to
    pick hex codes, but can override per-node if they want.

Spec shape (see examples/ for full files):

    {
      "chart_type": "sankey",
      "title": "...", "subtitle": "...", "source": "...",
      "value_format": ",.0f", "value_prefix": "$", "value_suffix": "",
      "show_values_in_labels": true,
      "nodes": [ {"id": "a", "label": "Revenue", "color": "#optional"} , ... ],
      "links": [ {"source": "a", "target": "b", "value": 1200} , ... ]
    }

Nodes are referenced by `id`. If `label` is omitted the id is used. Links point
at node ids; pointing at an unknown id is an error with a clear message rather
than a silent misdraw.
"""

from __future__ import annotations

from collections import deque

import plotly.graph_objects as go

from .base import apply_titles, format_value, register
from theme import color_for_index, hex_to_rgba


def _resolve_highlight(spec, nodes, idx):
    """
    Return the set of node indices to emphasize, or None.

    `highlight` accepts node ids, node labels, or integer indices (or a list of
    any mix). When set, the chart drops into "one accent + muted" mode — the a16z
    move where everything fades to a neutral tint and only the story path keeps
    color, exactly like a single highlighted bar.
    """
    raw = spec.get("highlight")
    if raw is None:
        return None
    if not isinstance(raw, list):
        raw = [raw]
    labels = {node.get("label", node["id"]): i for i, node in enumerate(nodes)}
    wanted = set()
    for item in raw:
        if isinstance(item, int) and 0 <= item < len(nodes):
            wanted.add(item)
        elif item in idx:
            wanted.add(idx[item])
        elif item in labels:
            wanted.add(labels[item])
    return wanted or None


def _build_node_index(nodes: list[dict]) -> dict[str, int]:
    index: dict[str, int] = {}
    for i, node in enumerate(nodes):
        node_id = node.get("id")
        if node_id is None:
            raise ValueError(f"Node #{i} is missing required 'id': {node!r}")
        if node_id in index:
            raise ValueError(f"Duplicate node id '{node_id}'")
        index[node_id] = i
    return index


def _node_throughput(nodes, links, idx) -> list[float]:
    """Throughput = max(total in, total out) — what the node actually carries."""
    inflow = [0.0] * len(nodes)
    outflow = [0.0] * len(nodes)
    for link in links:
        s = idx[link["source"]]
        t = idx[link["target"]]
        v = float(link["value"])
        outflow[s] += v
        inflow[t] += v
    return [max(inflow[i], outflow[i]) for i in range(len(nodes))]


def _auto_layout(n, links, idx):
    """
    Compute explicit (x, y) positions per node to minimize link crossings —
    the single biggest driver of a "spaghetti" Sankey. Plotly's default `snap`
    arrangement only honors the *input* order within each column, so without
    this every diagram inherits whatever order the data happened to be in.

    Two steps, both standard layered-graph techniques:
      1. Columns via longest-path layering (a node sits one column right of its
         deepest source), so flow is strictly left-to-right.
      2. Within each column, order nodes by the barycenter (mean position) of
         their neighbors, sweeping left→right then right→left a few times. This
         pulls connected nodes into vertical alignment so big flows travel
         straight across instead of crossing — the fix every Sankey guide
         recommends ("sort columns so links cross as little as possible").

    Returns (x, y) lists in [0,1]. We hand these to Plotly with
    arrangement="snap", which keeps our ordering but still spaces nodes by value
    so widths stay proportional.
    """
    # Neighbor lists carry the flow value so ordering is *volume-weighted*: a
    # node is pulled toward where its biggest flows go, so dominant ribbons run
    # straight and only thin flows bend.
    targets_of = {i: [] for i in range(n)}  # i -> [(target, value)]
    sources_of = {i: [] for i in range(n)}  # i -> [(source, value)]
    for link in links:
        s, t = idx[link["source"]], idx[link["target"]]
        v = float(link["value"])
        targets_of[s].append((t, v))
        sources_of[t].append((s, v))

    # --- 1. Longest-path layering (Kahn topological sweep) ---
    col = [0] * n
    indeg = [len(sources_of[i]) for i in range(n)]
    queue = deque(i for i in range(n) if indeg[i] == 0)
    while queue:
        u = queue.popleft()
        for v, _ in targets_of[u]:
            col[v] = max(col[v], col[u] + 1)
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    max_col = max(col) if col else 0

    columns: dict[int, list[int]] = {}
    for i in range(n):
        columns.setdefault(col[i], []).append(i)

    # --- 2. Volume-weighted barycenter ordering ---
    pos = {i: float(rank) for c in columns for rank, i in enumerate(columns[c])}

    def barycenter(i, neighbors):
        ns = neighbors[i]
        if not ns:
            return pos[i]
        total = sum(w for _, w in ns)
        return sum(pos[k] * w for k, w in ns) / total if total else pos[i]

    for _ in range(6):
        for c in sorted(columns):  # left -> right, order by sources
            if c == 0:
                continue
            columns[c].sort(key=lambda i: barycenter(i, sources_of))
            for rank, i in enumerate(columns[c]):
                pos[i] = float(rank)
        for c in sorted(columns, reverse=True):  # right -> left, order by targets
            if c == max_col:
                continue
            columns[c].sort(key=lambda i: barycenter(i, targets_of))
            for rank, i in enumerate(columns[c]):
                pos[i] = float(rank)

    # --- assign normalized coordinates (clamped off the exact edges) ---
    x = [0.5] * n
    y = [0.5] * n
    for c, members in columns.items():
        xc = 0.5 if max_col == 0 else c / max_col
        xc = min(max(xc, 0.001), 0.999)
        k = len(members)
        for rank, i in enumerate(members):
            x[i] = xc
            y[i] = min(max((rank + 0.5) / k, 0.001), 0.999)
    return x, y


@register("sankey")
def render(spec: dict, theme: dict) -> go.Figure:
    nodes = spec.get("nodes") or []
    links = spec.get("links") or []
    if not nodes:
        raise ValueError("Sankey spec needs a non-empty 'nodes' list")
    if not links:
        raise ValueError("Sankey spec needs a non-empty 'links' list")

    idx = _build_node_index(nodes)

    # Validate every link endpoint up front so a typo'd id surfaces as a clear
    # message instead of a raw KeyError deep in throughput/index code.
    for j, link in enumerate(links):
        for end in ("source", "target"):
            if link.get(end) not in idx:
                raise ValueError(
                    f"Link #{j} {end} '{link.get(end)}' is not a known node id. "
                    f"Known ids: {', '.join(idx)}"
                )

    # Color model:
    #  * default — each node a color from the (tight, harmonious) theme palette;
    #    flows inherit a soft tint of their source. Cohesive, not a rainbow.
    #  * highlight mode — when `highlight` names the story path, those nodes keep
    #    their palette color and everything else fades to the theme's muted tone,
    #    mirroring the "one bar that matters" look the bar charts use.
    highlight = _resolve_highlight(spec, nodes, idx)
    muted = theme.get("muted_color", "#9AA0A6")
    node_colors = []
    for i, node in enumerate(nodes):
        if node.get("color"):
            node_colors.append(node["color"])
        elif highlight is not None and i not in highlight:
            node_colors.append(muted)
        else:
            node_colors.append(color_for_index(theme, i))

    # Labels, optionally annotated with throughput so the graphic stands alone.
    show_values = spec.get("show_values_in_labels", True)
    throughput = _node_throughput(nodes, links, idx) if show_values else None
    labels = []
    for i, node in enumerate(nodes):
        name = node.get("label", node["id"])
        # Bold the name and drop the value onto its own line. Two short lines
        # read far cleaner over busy flows than one long "Name 1,234,567"
        # string, and the bold weight makes labels pop off the ribbons — the
        # main reason a default Plotly Sankey looks muddy.
        if show_values:
            text = f"<b>{name}</b><br>{format_value(throughput[i], spec)}"
        else:
            text = f"<b>{name}</b>"
        labels.append(text)

    # Resolve link endpoints to indices (already validated above).
    sources, targets, values, link_colors = [], [], [], []
    for link in links:
        s = idx[link["source"]]
        t = idx[link["target"]]
        sources.append(s)
        targets.append(t)
        values.append(float(link["value"]))
        if link.get("color"):
            link_colors.append(link["color"])
        elif highlight is not None and not (s in highlight and t in highlight):
            # In highlight mode a flow only stays colored when BOTH endpoints
            # are on the highlighted path — so a leak *out of* a highlighted
            # node (e.g. Activated → Churned) correctly fades to the neutral
            # wash, and only the story path keeps color.
            link_colors.append(hex_to_rgba(muted, theme["link_opacity"] * 0.6))
        else:
            # Flow tinted by its source node — the key readability move.
            link_colors.append(hex_to_rgba(node_colors[s], theme["link_opacity"]))

    # Hover text: clean "Source → Target: value" with the themed value format.
    link_hover = [
        f"{nodes[idx[l['source']]].get('label', l['source'])} → "
        f"{nodes[idx[l['target']]].get('label', l['target'])}: "
        f"{format_value(float(l['value']), spec)}"
        for l in links
    ]

    # Compute crossing-minimizing positions unless the caller opts out or has
    # hand-placed nodes (any node carrying explicit "x"/"y" disables auto-layout
    # so manual tuning is never silently overridden).
    manual = any("x" in node or "y" in node for node in nodes)
    use_auto = spec.get("auto_layout", True) and not manual
    if use_auto:
        node_x, node_y = _auto_layout(len(nodes), links, idx)
    elif manual:
        node_x = [node.get("x", 0.5) for node in nodes]
        node_y = [node.get("y", 0.5) for node in nodes]

    node_kwargs = dict(
        label=labels,
        color=node_colors,
        pad=theme["node_pad"],
        thickness=theme["node_thickness"],
        line=dict(
            color=theme["node_line_color"],
            width=theme["node_line_width"],
        ),
        hovertemplate="%{label}<extra></extra>",
    )
    if use_auto or manual:
        node_kwargs["x"] = node_x
        node_kwargs["y"] = node_y

    fig = go.Figure(
        go.Sankey(
            arrangement=spec.get("arrangement", "snap"),
            node=node_kwargs,
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
                customdata=link_hover,
                hovertemplate="%{customdata}<extra></extra>",
            ),
            textfont=dict(
                family=theme["font_family"],
                size=theme["label_size"],
                color=theme["font_color"],
            ),
        )
    )

    # Margins leave room for the title block (top) and source line (bottom).
    fig.update_layout(
        margin=dict(t=120, l=24, r=24, b=70),
        height=spec.get("height", 650),
        width=spec.get("width", 1100),
    )
    apply_titles(fig, spec, theme)
    return fig
