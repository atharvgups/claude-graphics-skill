"""
Choropleth map — values shaded across US states or world countries.

Uses Plotly's built-in geometries (no external GeoJSON): `scope: "usa"` takes
two-letter state codes; `scope: "world"` takes country names (or ISO-3 codes via
`"locationmode": "ISO-3"`). Editorial styling: sequential canvas→accent scale,
cream borders, no frame/coastline chrome.

Spec shape:

    {
      "chart_type": "choropleth", "scope": "usa",
      "locations": ["CA", "TX", "NY", ...],
      "z": [ 42, 38, 31, ... ],
      "value_suffix": "", "zmin": 0, "zmax": 50   // optional
    }
"""

from __future__ import annotations

import plotly.graph_objects as go

from .base import apply_titles, register
from theme import color_for_index, hex_to_rgba


@register("choropleth")
def render(spec: dict, theme: dict) -> go.Figure:
    locations = spec.get("locations") or []
    z = spec.get("z") or []
    if not locations or not z:
        raise ValueError("Choropleth needs 'locations' and 'z'")
    scope = spec.get("scope", "usa").lower()
    locmode = spec.get("locationmode") or (
        "USA-states" if scope == "usa" else "country names")
    accent = color_for_index(theme, 0)
    scale = spec.get("colorscale") or [[0, hex_to_rgba(accent, 0.12)],
                                       [1, accent]]
    sub = theme.get("subtitle_color", theme["font_color"])

    fig = go.Figure(go.Choropleth(
        locations=locations, z=z, locationmode=locmode, colorscale=scale,
        zmin=spec.get("zmin"), zmax=spec.get("zmax"),
        marker_line_color=theme["paper_bg"], marker_line_width=0.6,
        colorbar=dict(outlinewidth=0, len=0.7, thickness=14,
                      tickprefix=spec.get("value_prefix", ""),
                      ticksuffix=spec.get("value_suffix", ""),
                      tickfont=dict(family=theme["font_family"],
                                    size=theme["label_size"], color=sub)),
        hovertemplate="%{location}: %{z}<extra></extra>",
    ))
    fig.update_geos(
        scope=("usa" if scope == "usa" else "world"),
        showframe=False, showcoastlines=False, showland=True,
        landcolor=hex_to_rgba(theme["font_color"], 0.07),
        bgcolor=theme["paper_bg"], lakecolor=theme["paper_bg"],
        countrycolor=theme["paper_bg"], subunitcolor=theme["paper_bg"],
        projection_type=("albers usa" if scope == "usa" else "natural earth"),
    )
    fig.update_layout(
        margin=dict(t=130, l=20, r=20, b=70),
        height=spec.get("height", 640), width=spec.get("width", 1040),
        geo=dict(bgcolor=theme["paper_bg"]),
    )
    apply_titles(fig, spec, theme)
    return fig
