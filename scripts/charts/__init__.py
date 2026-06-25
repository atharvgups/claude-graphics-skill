"""
Chart renderers package.

Importing this package registers every available chart type by importing its
module (each module calls @register on import). To add a new chart type, create
a module here and add it to the import list below.
"""

from . import sankey   # noqa: F401  (registers "sankey")
from . import funnel   # noqa: F401  (registers "funnel")
from . import bar      # noqa: F401  (registers "bar" — single, grouped, stacked)
from . import line     # noqa: F401  (registers "line" — line + area)
from . import scatter  # noqa: F401  (registers "scatter" — incl. bubble)
from . import pie      # noqa: F401  (registers "pie" — pie + donut)
from . import combo    # noqa: F401  (registers "combo" — dual-axis bar+line)
from . import waterfall        # noqa: F401  (registers "waterfall")
from . import dot              # noqa: F401  (registers "dot" — lollipop/dumbbell)
from . import heatmap          # noqa: F401  (registers "heatmap")
from . import treemap          # noqa: F401  (registers "treemap")
from . import small_multiples  # noqa: F401  (registers "small_multiples")
from . import histogram        # noqa: F401  (registers "histogram")
from . import box              # noqa: F401  (registers "box" — box/violin)
from . import radar            # noqa: F401  (registers "radar")
from . import slope            # noqa: F401  (registers "slope")
from . import bump             # noqa: F401  (registers "bump")
from . import candlestick      # noqa: F401  (registers "candlestick")
from . import table            # noqa: F401  (registers "table")
from . import hierarchy        # noqa: F401  (registers "sunburst")
from . import indicator        # noqa: F401  (registers "bignumber" + "gauge" + "bullet")
from . import marimekko        # noqa: F401  (registers "marimekko")
from . import pyramid          # noqa: F401  (registers "pyramid")
from . import choropleth       # noqa: F401  (registers "choropleth")
from . import pictograph       # noqa: F401  (registers "pictograph")

# Future chart types plug in the same way, e.g.:
# from . import network  # noqa: F401
