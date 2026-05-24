"""
============================================================
  Pokémon GO Player Insights — APEXJBS
  Raw game data → readable portfolio visualizations
  
  Outputs:
    1. pokemon_go_dashboard.png  — multi-panel summary poster
    2. pokemon_go_map.html       — interactive Folium heatmap
============================================================

SETUP
-----
1. Put all your .tsv files in one folder
2. Update DATA_DIR below to point to that folder
3. Run:  python3 pokemon_go_insights.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import folium
from folium.plugins import HeatMap
import warnings
warnings.filterwarnings('ignore')

# ── ❶  EDIT THIS PATH ────────────────────────────────────────────────────────
DATA_DIR = "."   # folder containing your .tsv files; "." = same folder as script
OUTPUT_DIR = "." # where to save the output files
# ─────────────────────────────────────────────────────────────────────────────

# ── Color palette (vibrant game theme) ───────────────────────────────────────
BG       = "#0D0D1A"
PANEL    = "#13132A"
YELLOW   = "#FFD700"
ELECTRIC = "#F7FF00"
FIRE     = "#FF6B35"
WATER    = "#00B4FF"
PSYCHIC  = "#FF3CAC"
GRASS    = "#39FF14"
GHOST    = "#9B59FF"
WHITE    = "#F0F0FF"
MUTED    = "#5A5A8A"

plt.rcParams.update({
    "font.family":      "monospace",
    "text.color":       WHITE,
    "axes.facecolor":   PANEL,
    "figure.facecolor": BG,
    "axes.edgecolor":   MUTED,
    "axes.labelcolor":  WHITE,
    "xtick.color":      MUTED,
    "ytick.color":      MUTED,
    "grid.color":       "#1E1E3A",
    "grid.linewidth":   0.6,
})

# ── Load data ─────────────────────────────────────────────────────────────────
def load(filename):
    return pd.read_csv(os.path.join(DATA_DIR, filename), sep='\t')

print("Loading data...")

# Fitness
fit = load("FitnessData.tsv")
fit['dt']   = pd.to_datetime(fit['Date and time of logging (UTC)'])
fit['date'] = fit['dt'].dt.date.astype(str)
daily = fit.groupby('date').agg({
    'Steps walked':                  'sum',
    'Calories burned':               'sum',
    'Distance travelled (meters)':   'sum',
}).reset_index()
daily['km'] = daily['Distance travelled (meters)'] / 1000

# Purchases
iap = load("InAppPurchases.tsv")
iap['dt']   = pd.to_datetime(iap['Date and time'], format='%m/%d/%Y %H:%M:%S UTC', errors='coerce')
iap['year'] = iap['dt'].dt.year
spent       = iap[iap['Change in pokecoins'] < 0].copy()
spent['coins'] = spent['Change in pokecoins'].abs()
by_year     = spent.groupby('year')['coins'].sum().reset_index()

# Friends
friends    = load("FriendList.tsv")
friends['dt']   = pd.to_datetime(friends['Date of friendship start'])
friends['year'] = friends['dt'].dt.year
friend_yr  = friends.groupby('year').size().reset_index(name='count')
friend_yr['cumulative'] = friend_yr['count'].cumsum()

# Locations
loc = load("GameplayLocationHistory.tsv")
loc.columns = ['timestamp', 'lat', 'lon']
loc['dt']   = pd.to_datetime(loc['timestamp'])
loc['hour'] = loc['dt'].dt.hour
hour_counts = loc.groupby('hour').size().reindex(range(24), fill_value=0).reset_index()
hour_counts.columns = ['hour', 'count']

# Top items (clean names)
item_map = {
    'POKECOIN':                    'PokéCoins',
    'Poke balls':                  'Poké Balls',
    'LPSKU_BUNDLE.GENERAL1.FREE.': 'Free Daily Bundle',
    'Great balls':                 'Great Balls',
    'Potion':                      'Potions',
    'Razz berry':                  'Razz Berries',
    'ITEM_REMOTE_RAID_TICKET':     'Remote Raid Pass',
    'Pokemon storage upgrade':     'Storage Upgrade',
}
raw_items = iap[iap['Item purchased'].notna()]['Item purchased'].value_counts().head(8)
items_df  = pd.DataFrame({'raw': raw_items.index, 'count': raw_items.values})
items_df['label'] = items_df['raw'].map(item_map).fillna(items_df['raw'])

print("Building dashboard poster...")

# ═══════════════════════════════════════════════════════════════════════════════
#   FIGURE 1 — Dashboard poster
# ═══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(20, 24), facecolor=BG)
fig.patch.set_facecolor(BG)

gs = gridspec.GridSpec(
    5, 3,
    figure=fig,
    hspace=0.55,
    wspace=0.35,
    top=0.92, bottom=0.04,
    left=0.06, right=0.97,
)

# ── Header ────────────────────────────────────────────────────────────────────
ax_header = fig.add_subplot(gs[0, :])
ax_header.set_facecolor(BG)
ax_header.axis('off')

ax_header.text(
    0.0, 0.85, "POKÉMON GO",
    transform=ax_header.transAxes,
    fontsize=42, fontweight='bold', fontfamily='monospace',
    color=YELLOW,
    path_effects=[pe.withStroke(linewidth=6, foreground='#7A5800')]
)
ax_header.text(
    0.0, 0.30, "PLAYER INSIGHTS  ·  APEXJBS  ·  2018 – 2026",
    transform=ax_header.transAxes,
    fontsize=14, fontfamily='monospace', color=MUTED,
)

# Stat pills
stats = [
    ("130,873",  "STEPS WALKED",    ELECTRIC),
    ("117.7 km", "DISTANCE",        WATER),
    ("3,338",    "CALORIES BURNED", FIRE),
    ("23,962",   "POKÉCOINS SPENT", YELLOW),
    ("179",      "FRIENDS",         PSYCHIC),
    ("3,341",    "GPS POINTS",      GRASS),
]
for i, (val, label, col) in enumerate(stats):
    x = 0.0 + i * 0.168
    rect = FancyBboxPatch((x, -0.18), 0.155, 0.32,
                          boxstyle="round,pad=0.01",
                          linewidth=1.5, edgecolor=col,
                          facecolor=BG,
                          transform=ax_header.transAxes, clip_on=False)
    ax_header.add_patch(rect)
    ax_header.text(x + 0.077, -0.01, val,
                   transform=ax_header.transAxes,
                   ha='center', va='center',
                   fontsize=15, fontweight='bold', color=col, fontfamily='monospace')
    ax_header.text(x + 0.077, -0.13, label,
                   transform=ax_header.transAxes,
                   ha='center', va='center',
                   fontsize=7.5, color=MUTED, fontfamily='monospace')

# ── Panel helper ─────────────────────────────────────────────────────────────
def panel_title(ax, title, color=YELLOW):
    ax.text(0.0, 1.06, title,
            transform=ax.transAxes,
            fontsize=11, fontweight='bold', color=color, fontfamily='monospace')
    ax.axhline(y=ax.get_ylim()[1] if hasattr(ax, '_yaxis_initialized') else 0,
               color=color, linewidth=0.5, alpha=0.3)

# ── 1. Daily Steps ────────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[1, :2])
x    = np.arange(len(daily))
bars = ax1.bar(x, daily['Steps walked'], color=ELECTRIC, alpha=0.85, width=0.75, zorder=3)

avg = daily['Steps walked'].mean()
for bar, val in zip(bars, daily['Steps walked']):
    bar.set_color(GRASS if val >= avg else ELECTRIC)
    bar.set_alpha(0.85)

ax1.axhline(avg, color=FIRE, linewidth=1.5, linestyle='--', zorder=4, label=f'avg {avg:,.0f}')
ax1.set_xticks(x[::2])
ax1.set_xticklabels([d[5:] for d in daily['date'].iloc[::2]], fontsize=8, rotation=45)
ax1.set_ylabel("Steps", fontsize=9, color=MUTED)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{int(v):,}'))
ax1.legend(fontsize=8, facecolor=PANEL, edgecolor=MUTED, labelcolor=WHITE)
ax1.grid(axis='y', zorder=0)
ax1.set_title("DAILY STEPS  — Apr 25 → May 17, 2026",
              fontsize=10, color=YELLOW, fontfamily='monospace', pad=10)

# ── 2. Calories ───────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 2])
ax2.fill_between(x, daily['Calories burned'], color=FIRE, alpha=0.6, zorder=3)
ax2.plot(x, daily['Calories burned'], color=FIRE, linewidth=2, zorder=4)
ax2.set_xticks(x[::4])
ax2.set_xticklabels([d[5:] for d in daily['date'].iloc[::4]], fontsize=8, rotation=45)
ax2.set_ylabel("Calories", fontsize=9, color=MUTED)
ax2.grid(axis='y', zorder=0)
ax2.set_title("CALORIES BURNED", fontsize=10, color=FIRE, fontfamily='monospace', pad=10)

# ── 3. PokéCoin Spending ──────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2, :2])
colors_yr = [GHOST if y != 2023 else PSYCHIC for y in by_year['year']]
bars3 = ax3.bar(by_year['year'].astype(str), by_year['coins'],
                color=colors_yr, alpha=0.9, width=0.6, zorder=3)

for bar, val in zip(bars3, by_year['coins']):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
             f'{int(val):,}', ha='center', fontsize=8.5,
             color=WHITE, fontfamily='monospace')

ax3.set_ylabel("PokéCoins", fontsize=9, color=MUTED)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{int(v):,}'))
ax3.grid(axis='y', zorder=0)
ax3.set_title("POKÉCOIN SPENDING BY YEAR  (peak: 2023)",
              fontsize=10, color=PSYCHIC, fontfamily='monospace', pad=10)

ax3.annotate('no data\n2020', xy=('2021', 100), xytext=('2021', 3000),
             fontsize=7.5, color=MUTED, ha='center', fontfamily='monospace',
             arrowprops=dict(arrowstyle='->', color=MUTED, lw=0.8))

# ── 4. Play Time by Hour ──────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 2], polar=False)
hour_colors = [WATER if 6 <= h <= 20 else GHOST for h in hour_counts['hour']]
ax4.bar(hour_counts['hour'], hour_counts['count'],
        color=hour_colors, alpha=0.85, width=0.8, zorder=3)
ax4.set_xticks([0, 6, 12, 18, 23])
ax4.set_xticklabels(['12am','6am','12pm','6pm','11pm'], fontsize=8)
ax4.set_ylabel("GPS pings", fontsize=9, color=MUTED)
ax4.grid(axis='y', zorder=0)
ax4.set_title("PLAY TIME BY HOUR", fontsize=10, color=WATER, fontfamily='monospace', pad=10)

day_patch   = mpatches.Patch(color=WATER,  label='Daytime')
night_patch = mpatches.Patch(color=GHOST,  label='Night owl')
ax4.legend(handles=[day_patch, night_patch], fontsize=7.5,
           facecolor=PANEL, edgecolor=MUTED, labelcolor=WHITE)

# ── 5. Friends Growth ─────────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[3, :2])
ax5.fill_between(friend_yr['year'], friend_yr['cumulative'],
                 color=PSYCHIC, alpha=0.25, zorder=2)
ax5.plot(friend_yr['year'], friend_yr['cumulative'],
         color=PSYCHIC, linewidth=3, marker='o',
         markersize=10, markerfacecolor=BG,
         markeredgecolor=PSYCHIC, markeredgewidth=2.5, zorder=3)

for _, row in friend_yr.iterrows():
    ax5.annotate(f"+{int(row['count'])}",
                 xy=(row['year'], row['cumulative']),
                 xytext=(0, 14), textcoords='offset points',
                 ha='center', fontsize=9, color=PSYCHIC, fontfamily='monospace')

ax5.set_xticks(friend_yr['year'])
ax5.set_ylabel("Total friends", fontsize=9, color=MUTED)
ax5.grid(axis='y', zorder=0)
ax5.set_title("FRIEND NETWORK GROWTH",
              fontsize=10, color=PSYCHIC, fontfamily='monospace', pad=10)

# ── 6. Top Items ──────────────────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[3, 2])
item_colors = [YELLOW, ELECTRIC, GRASS, WATER, FIRE, GHOST, PSYCHIC, FIRE]
bars6 = ax6.barh(items_df['label'][::-1], items_df['count'][::-1],
                 color=item_colors[:len(items_df)][::-1],
                 alpha=0.85, height=0.65, zorder=3)
for bar, val in zip(bars6, items_df['count'][::-1]):
    ax6.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
             f'{int(val)}', va='center', fontsize=8, color=WHITE, fontfamily='monospace')
ax6.set_xlabel("Times acquired", fontsize=9, color=MUTED)
ax6.grid(axis='x', zorder=0)
ax6.set_title("TOP ITEMS", fontsize=10, color=YELLOW, fontfamily='monospace', pad=10)

# ── 7. GPS Dot Map ────────────────────────────────────────────────────────────
ax7 = fig.add_subplot(gs[4, :])
ax7.set_facecolor("#080810")

from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list(
    'poke', [GHOST, WATER, GRASS, ELECTRIC, YELLOW], N=256)

lat_bins = np.linspace(loc['lat'].min(), loc['lat'].max(), 120)
lon_bins = np.linspace(loc['lon'].min(), loc['lon'].max(), 120)
H, xedges, yedges = np.histogram2d(loc['lon'], loc['lat'], bins=[lon_bins, lat_bins])
H = np.log1p(H)

extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
im = ax7.imshow(H.T, extent=extent, origin='lower', cmap=cmap,
                aspect='auto', alpha=0.92, interpolation='gaussian')

ax7.scatter(loc['lon'], loc['lat'], s=0.8, c=ELECTRIC, alpha=0.07, zorder=2)

ax7.set_xlabel("Longitude", fontsize=9, color=MUTED)
ax7.set_ylabel("Latitude", fontsize=9, color=MUTED)
ax7.set_title("GAMEPLAY LOCATION HEATMAP  — Boston / Northeast Corridor  (3,341 GPS points)",
              fontsize=10, color=GRASS, fontfamily='monospace', pad=10)

cbar = plt.colorbar(im, ax=ax7, orientation='vertical', fraction=0.015, pad=0.01)
cbar.set_label('Activity density (log)', fontsize=8, color=MUTED)
cbar.ax.yaxis.set_tick_params(color=MUTED, labelsize=7)
plt.setp(cbar.ax.yaxis.get_ticklabels(), color=MUTED)

# ── Footer ────────────────────────────────────────────────────────────────────
fig.text(0.06, 0.015,
         "Data source: Pokémon GO personal data export  ·  Visualization: Python (matplotlib)  ·  github.com/APEXJBS",
         fontsize=8, color=MUTED, fontfamily='monospace')

# ── Save poster ───────────────────────────────────────────────────────────────
poster_path = os.path.join(OUTPUT_DIR, "pokemon_go_dashboard.png")
plt.savefig(poster_path, dpi=180, bbox_inches='tight', facecolor=BG)
plt.close()
print(f"✅  Saved: {poster_path}")


# ═══════════════════════════════════════════════════════════════════════════════
#   FIGURE 2 — Interactive Folium map
# ═══════════════════════════════════════════════════════════════════════════════
print("Building interactive map...")

center_lat = loc['lat'].mean()
center_lon = loc['lon'].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=11,
    tiles='CartoDB dark_matter',
)

heat_data = list(zip(loc['lat'], loc['lon']))
HeatMap(
    heat_data,
    radius=12,
    blur=16,
    max_zoom=15,
    gradient={
        0.2: '#9B59FF',
        0.4: '#00B4FF',
        0.6: '#39FF14',
        0.8: '#F7FF00',
        1.0: '#FFD700',
    }
).add_to(m)

title_html = """
<div style="
    position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
    background: rgba(13,13,26,0.92); color: #FFD700;
    font-family: monospace; font-size: 16px; font-weight: bold;
    padding: 10px 24px; border-radius: 8px;
    border: 1.5px solid #FFD700; z-index: 9999;
    letter-spacing: 2px; pointer-events: none;">
    APEXJBS · POKÉMON GO PLAY LOCATIONS
</div>
"""
m.get_root().html.add_child(folium.Element(title_html))

map_path = os.path.join(OUTPUT_DIR, "pokemon_go_map.html")
m.save(map_path)
print(f"✅  Saved: {map_path}")

print("\n🎮  Done! Open pokemon_go_map.html in your browser for the interactive map.")
print("    pokemon_go_dashboard.png is your portfolio poster.")