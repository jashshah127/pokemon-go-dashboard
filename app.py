import pandas as pd
# app.py
# Pokemon GO Player Dashboard — APEXJBS
# Run: python3 app.py → open http://localhost:8050

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import folium
from folium.plugins import HeatMap
import os
from data_loader import load_all, TYPE_COLORS

D = load_all()

# ── Colors ────────────────────────────────────────────────────────────────────
BG      = '#0F1117'
PANEL   = '#1A1D2E'
BORDER  = '#2A2D3E'
TEXT    = '#E8E8F0'
MUTED   = '#6B7280'
ACCENT  = '#6366F1'   # indigo
YELLOW  = '#F59E0B'   # amber
FIRE    = '#EF4444'   # red
WATER   = '#3B82F6'   # blue
GRASS   = '#10B981'   # emerald
PSYCHIC = '#EC4899'   # pink
GHOST   = '#8B5CF6'   # violet
ELECTRIC= '#EAB308'   # yellow
WHITE   = '#F9FAFB'

CHART = dict(
    paper_bgcolor=BG,
    plot_bgcolor=PANEL,
    font=dict(family='Inter, system-ui, sans-serif', color=TEXT, size=12),
    margin=dict(t=50, b=40, l=50, r=20),
    legend=dict(bgcolor=PANEL, bordercolor=BORDER, font=dict(color=TEXT)),
)
AX = dict(gridcolor=BORDER, showgrid=True, zeroline=False)

app = dash.Dash(
    __name__,
    title='APEXJBS — Pokemon GO',
    external_stylesheets=['https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'],
    meta_tags=[{'name':'viewport','content':'width=device-width, initial-scale=1'}]
)

# ── Style helpers ─────────────────────────────────────────────────────────────
CARD = {
    'background': PANEL,
    'border': f'1px solid {BORDER}',
    'borderRadius': '12px',
    'padding': '20px',
    'marginBottom': '16px',
}

def kpi(label, value, color=ACCENT, sub=None):
    return html.Div([
        html.Div(value, style={
            'fontSize':'24px','fontWeight':'700',
            'color': color,'fontFamily':'Inter, sans-serif',
            'lineHeight':'1.2',
        }),
        html.Div(label, style={
            'fontSize':'11px','color':MUTED,'fontFamily':'Inter, sans-serif',
            'marginTop':'4px','textTransform':'uppercase','letterSpacing':'0.08em',
        }),
        html.Div(sub, style={'fontSize':'11px','color':MUTED,'marginTop':'2px'}) if sub else None,
    ], style={
        'background': PANEL,'border': f'1px solid {BORDER}',
        'borderTop': f'3px solid {color}','borderRadius':'10px',
        'padding':'16px 18px','flex':'1','minWidth':'120px',
    })

def stitle(text, color=ACCENT):
    return html.Div(text, style={
        'color': color,'fontFamily':'Inter, sans-serif',
        'fontSize':'12px','fontWeight':'600','letterSpacing':'0.06em',
        'textTransform':'uppercase','marginBottom':'14px',
        'paddingBottom':'8px','borderBottom':f'1px solid {BORDER}',
    })

TAB_S = {
    'backgroundColor': PANEL,'color': MUTED,
    'border': f'1px solid {BORDER}','borderRadius':'8px 8px 0 0',
    'padding':'10px 16px','fontFamily':'Inter, sans-serif','fontSize':'13px',
    'fontWeight':'500',
}
TAB_SEL = {
    **TAB_S,'backgroundColor': BG,'color': WHITE,
    'borderBottom': f'2px solid {ACCENT}','fontWeight':'600',
}

ROW = {'display':'flex','gap':'16px','marginBottom':'0'}

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
def tab_overview():
    s = D['stats']

    enc_m   = D['encounters'].groupby('month').size().reset_index(name='Encounters')
    ps_m    = D['pokestops'].groupby('month').size().reset_index(name='Pokestop Spins')
    raids_m = D['raids'].groupby('month').size().reset_index(name='Raids')
    gyms_m  = D['battles'].groupby('month').size().reset_index(name='Gym Battles')
    tl = enc_m.merge(ps_m,on='month',how='outer')\
               .merge(raids_m,on='month',how='outer')\
               .merge(gyms_m,on='month',how='outer')\
               .fillna(0).sort_values('month')

    fig_tl = go.Figure()
    for col, color in zip(
        ['Encounters','Pokestop Spins','Raids','Gym Battles'],
        [ACCENT, WATER, FIRE, GRASS]
    ):
        fig_tl.add_trace(go.Scatter(
            x=tl['month'], y=tl[col], name=col,
            mode='lines+markers',
            line=dict(color=color, width=2),
            marker=dict(size=4),
            hovertemplate=f'%{{x}}<br>{col}: %{{y:,.0f}}<extra></extra>'
        ))
    fig_tl.update_layout(**CHART,
        title=dict(text='Activity Timeline — All Event Types', font=dict(color=TEXT,size=13)),
        height=340)
    fig_tl.update_xaxes(**AX, tickangle=45)
    fig_tl.update_yaxes(**AX)

    enc_yr = D['encounters'].groupby('year').size().reset_index(name='count')
    fig_yr = go.Figure(go.Bar(
        x=enc_yr['year'].astype(str), y=enc_yr['count'],
        marker_color=[BORDER if y!=2026 else ACCENT for y in enc_yr['year']],
        text=enc_yr['count'].apply(lambda v:f'{v:,}'),
        textposition='outside', textfont=dict(color=TEXT, size=11),
        hovertemplate='%{x}<br>%{y:,} encounters<extra></extra>',
    ))
    fig_yr.update_layout(**CHART,
        title=dict(text='Encounters by Year', font=dict(color=TEXT,size=13)),
        height=300, showlegend=False)
    fig_yr.update_xaxes(**AX)
    fig_yr.update_yaxes(**AX)

    return html.Div([
        html.Div([
            kpi('Level',         str(s['level']),              ACCENT),
            kpi('Total XP',      f"{s['xp']:,}",               YELLOW),
            kpi('Lifetime km',   f"{s['distance_km']:,.1f}",   WATER),
            kpi('In Storage',    str(s['total_pokemon']),       GRASS,  'Pokémon'),
            kpi('Species',       str(s['unique_species']),      FIRE,   'Unique'),
            kpi('Eggs Hatched',  str(s['eggs_hatched']),        PSYCHIC),
            kpi('Stardust',      f"{s['stardust']:,}",          GHOST),
            kpi('Playing Since', s['start_date'],               MUTED),
        ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'}),

        html.Div([
            kpi('Map Encounters', f"{len(D['encounters']):,}",  ACCENT),
            kpi('Pokéstop Spins', f"{len(D['pokestops']):,}",   WATER),
            kpi('Raids Joined',   f"{len(D['raids']):,}",       FIRE),
            kpi('Gym Battles',    f"{len(D['battles']):,}",     GRASS),
            kpi('Gym Deploys',    f"{len(D['deploys']):,}",     ELECTRIC),
            kpi('Berries Fed',    f"{len(D['feed']):,}",        PSYCHIC),
            kpi('Friends',        str(len(D['friends'])),       GHOST),
            kpi('Buddy',          s['buddy'],                   MUTED),
        ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'}),

        html.Div([
            html.Div([
                stitle('Activity Timeline'),
                dcc.Graph(figure=fig_tl, config={'displayModeBar':False}),
            ], style={**CARD,'flex':'2'}),
            html.Div([
                stitle('Year Over Year'),
                dcc.Graph(figure=fig_yr, config={'displayModeBar':False}),
            ], style={**CARD,'flex':'1'}),
        ], style=ROW),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 2 — POKEMON
# ─────────────────────────────────────────────────────────────────────────────
def tab_pokemon():
    # ── KPI row ───────────────────────────────────────────────────────────────
    s = D['stats']
    kpi_row = html.Div([
        kpi('In Storage',     str(s['total_pokemon']),    ACCENT,   'Pokémon'),
        kpi('Unique Species', str(s['unique_species']),   GRASS,    'Distinct'),
        kpi('Legendaries',    '52',                        YELLOW,   '36 unique'),
        kpi('Mythicals',      '10',                        FIRE,     '7 unique'),
        kpi('Eggs Hatched',   str(s['eggs_hatched']),      WATER,    'Total'),
        kpi('Stardust',       f"{s['stardust']:,}",        GHOST),
        kpi('Buddy',          s['buddy'],                  PSYCHIC),
        kpi('Master Ball',    '1',                         ELECTRIC, 'Remaining'),
    ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'})

    # ── Top 25 species ────────────────────────────────────────────────────────
    top = D['collection'].head(25)
    fig_top = go.Figure(go.Bar(
        x=top['count'], y=top['pokemon'],
        orientation='h',
        marker_color=ACCENT, marker_opacity=0.9,
        text=top['count'], textposition='outside',
        textfont=dict(color=TEXT, size=11),
        hovertemplate='%{y}<br>%{x} in storage<extra></extra>',
    ))
    fig_top.update_layout(**CHART,
        title=dict(text='Top 25 Most Common Pokémon in Storage', font=dict(color=TEXT,size=13)),
        height=520, showlegend=False)
    fig_top.update_xaxes(**AX)
    fig_top.update_yaxes(autorange='reversed', gridcolor=BORDER)

    # ── Type distribution donut ───────────────────────────────────────────────
    types = D['types']
    fig_donut = go.Figure(go.Pie(
        labels=types['type'],
        values=types['count'],
        hole=0.55,
        marker_colors=types['color'].tolist(),
        textfont=dict(family='Inter', color=WHITE, size=11),
        hovertemplate='%{label}<br>%{value} Pokémon (%{percent})<extra></extra>',
        textinfo='label+value',
    ))
    fig_donut.update_layout(**CHART,
        title=dict(text='Type Distribution — Your Storage', font=dict(color=TEXT,size=13)),
        height=520,
    )

    # ── Legendaries bar ───────────────────────────────────────────────────────
    leg_data = {
        'Kyogre':4,'Thundurus':4,'Tapu Fini':3,'Genesect':3,
        'Ho-Oh':2,'Giratina':2,'Latios':2,'Mesprit':2,'Moltres':2,
        'Necrozma':2,'Tapu Bulu':2,'Buzzwole':2,'Articuno':1,'Azelf':1,
        'Blacephalon':1,'Cobalion':1,'Dialga':1,'Enamorus':1,'Kubfu':1,
        'Kyurem':1,'Landorus':1,'Latias':1,'Mewtwo':1,'Nihilego':1,
        'Palkia':1,'Pheromosa':1,'Rayquaza':1,'Regigigas':1,'Regirock':1,
        'Registeel':1,'Stakataka':1,'Tapu Koko':1,'Terrakion':1,
        'Tornadus':1,'Ursaluna':1,'Uxie':1,'Zacian':1,
    }
    leg_df = pd.DataFrame(list(leg_data.items()), columns=['name','count']).sort_values('count',ascending=True)
    fig_leg = go.Figure(go.Bar(
        x=leg_df['count'], y=leg_df['name'],
        orientation='h',
        marker_color=YELLOW, marker_opacity=0.85,
        text=leg_df['count'], textposition='outside',
        textfont=dict(color=TEXT, size=11),
        hovertemplate='%{y}<br>×%{x} in storage<extra></extra>',
    ))
    fig_leg.update_layout(**CHART,
        title=dict(text='Legendaries in Storage — 52 total, 36 unique', font=dict(color=TEXT,size=13)),
        height=680, showlegend=False)
    fig_leg.update_xaxes(**AX)
    fig_leg.update_yaxes(gridcolor=BORDER)

    # ── Mythicals ─────────────────────────────────────────────────────────────
    myth_data = {'Genesect':4,'Celebi':1,'Jirachi':1,'Kubfu':1,'Shaymin':1,'Victini':1,'Volcanion':1}
    myth_df = pd.DataFrame(list(myth_data.items()), columns=['name','count']).sort_values('count',ascending=True)
    fig_myth = go.Figure(go.Bar(
        x=myth_df['count'], y=myth_df['name'],
        orientation='h',
        marker_color=PSYCHIC, marker_opacity=0.85,
        text=myth_df['count'], textposition='outside',
        textfont=dict(color=TEXT, size=11),
        hovertemplate='%{y}<br>×%{x}<extra></extra>',
    ))
    fig_myth.update_layout(**CHART,
        title=dict(text='Mythicals in Storage — 10 total, 7 unique', font=dict(color=TEXT,size=13)),
        height=280, showlegend=False)
    fig_myth.update_xaxes(**AX)
    fig_myth.update_yaxes(gridcolor=BORDER)

    # ── Medal catch levels ────────────────────────────────────────────────────
    type_medals = {
        'Bug':4,'Fire':4,'Flying':4,'Grass':4,'Normal':4,'Poison':4,
        'Psychic':4,'Water':4,'Dark':3,'Dragon':3,'Electric':3,'Fairy':3,
        'Fighting':3,'Ghost':3,'Ground':3,'Ice':3,'Rock':3,'Steel':3,
    }
    medal_labels = {1:'Bronze',2:'Silver',3:'Gold',4:'Platinum'}
    medal_colors_map = {1:FIRE, 2:MUTED, 3:YELLOW, 4:WATER}
    tm_df = pd.DataFrame([
        {'type':t,'level':l,'label':medal_labels[l],'color':medal_colors_map[l]}
        for t,l in type_medals.items()
    ]).sort_values(['level','type'], ascending=[False,True])

    fig_medals = go.Figure()
    for lvl, label, color in [(4,'Platinum',WATER),(3,'Gold',YELLOW),(2,'Silver',MUTED),(1,'Bronze',FIRE)]:
        df = tm_df[tm_df['level']==lvl]
        if len(df)==0: continue
        fig_medals.add_trace(go.Bar(
            x=df['type'], y=[lvl]*len(df),
            name=label,
            marker_color=color, opacity=0.85,
            hovertemplate=f'%{{x}} — {label} Medal<extra></extra>',
        ))
    fig_medals.update_layout(**CHART, barmode='stack',
        title=dict(text='Type Catch Medal Levels', font=dict(color=TEXT,size=13)),
        height=280)
    fig_medals.update_xaxes(**AX, tickangle=45)
    fig_medals.update_yaxes(
        tickvals=[1,2,3,4],
        ticktext=['Bronze','Silver','Gold','Platinum'],
        gridcolor=BORDER
    )

    # ── Key items inventory ───────────────────────────────────────────────────
    key_items = [
        ('Max Revive',362,FIRE),('Max Potion',357,WATER),('Revive',304,GRASS),
        ('Pinap Berry',295,GRASS),('Hyper Potion',274,WATER),('Charged TM',193,ACCENT),
        ('Golden Razz',172,YELLOW),('Fast TM',147,ACCENT),('Golden Pinap',136,YELLOW),
        ('Incense',42,GHOST),('Star Piece',28,FIRE),('Poffin',18,PSYCHIC),
        ('Ultra Ball',15,WATER),('Lucky Egg',14,ELECTRIC),('Shadow Gem',12,GHOST),
        ('Elite Charged TM',8,YELLOW),('Elite Fast TM',7,YELLOW),
        ('Raid Pass',11,FIRE),('Remote Raid',3,FIRE),('Master Ball',1,ELECTRIC),
    ]
    items_df2 = pd.DataFrame(key_items, columns=['item','qty','color'])
    fig_items = go.Figure(go.Bar(
        x=items_df2['qty'], y=items_df2['item'],
        orientation='h',
        marker_color=items_df2['color'].tolist(),
        marker_opacity=0.85,
        text=items_df2['qty'], textposition='outside',
        textfont=dict(color=TEXT, size=11),
        hovertemplate='%{y}<br>%{x:,}<extra></extra>',
    ))
    fig_items.update_layout(**CHART,
        title=dict(text='Key Item Inventory', font=dict(color=TEXT,size=13)),
        height=560, showlegend=False)
    fig_items.update_xaxes(**AX)
    fig_items.update_yaxes(autorange='reversed', gridcolor=BORDER)

    # ── Team Rocket section ───────────────────────────────────────────────────
    rocket_cards = html.Div([
        stitle('🚀 Team Rocket Activity', FIRE),
        html.Div([
            kpi('Grunts Defeated',   'Platinum (Lv 4)', FIRE),
            kpi('Giovanni Defeated', 'Silver (Lv 2)',   GHOST),
            kpi('Pokémon Purified',  'Silver (Lv 2)',   PSYCHIC),
            kpi('Shadow Gems',       '12',               GHOST),
            kpi('Shadow Gem Frags',  '0',                MUTED),
        ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginTop':'12px'}),
        html.Div([
            html.P('You have defeated Giovanni multiple times and purified a significant number of Shadow Pokémon. '
                   'With 12 Shadow Gems in inventory, you are actively participating in Shadow Raids. '
                   'The Platinum grunt badge indicates hundreds of grunt battles fought.',
                   style={'color':MUTED,'fontFamily':'Inter','fontSize':'13px',
                          'lineHeight':'1.6','marginTop':'12px','margin':'12px 0 0 0'}),
        ]),
    ], style=CARD)

    # ── Recent catches ────────────────────────────────────────────────────────
    catches = D['catches']
    rows = []
    for _, r in catches.iterrows():
        tc = TYPE_COLORS.get(r.get('type',''), MUTED)
        mc = WATER if r['method']=='Hatched' else GRASS
        rows.append(html.Tr([
            html.Td(r['name'], style={'color':TEXT,'padding':'8px 12px','fontWeight':'500'}),
            html.Td(html.Span(r.get('type','?'), style={
                'background':tc+'22','color':tc,'padding':'2px 8px',
                'borderRadius':'4px','fontSize':'11px','fontWeight':'600',
            }), style={'padding':'8px 12px'}),
            html.Td(f"CP {r['cp']}", style={'color':YELLOW,'padding':'8px 12px','fontWeight':'700'}),
            html.Td(html.Span(r['method'], style={
                'background':mc+'22','color':mc,'padding':'2px 8px',
                'borderRadius':'4px','fontSize':'11px',
            }), style={'padding':'8px 12px'}),
            html.Td(str(r['timestamp'])[:16], style={'color':MUTED,'padding':'8px 12px','fontSize':'11px'}),
        ], style={'borderBottom':f'1px solid {BORDER}'}))

    catch_table = html.Div([
        stitle('Last Session Catches — May 18 2026', FIRE),
        html.Table([
            html.Thead(html.Tr([
                html.Th(h, style={'color':MUTED,'padding':'8px 12px','textAlign':'left',
                                  'fontSize':'11px','fontWeight':'600','textTransform':'uppercase'})
                for h in ['Pokémon','Type','CP','Method','Time']
            ], style={'borderBottom':f'2px solid {BORDER}'})),
            html.Tbody(rows)
        ], style={'width':'100%','borderCollapse':'collapse',
                  'fontFamily':'Inter, sans-serif','fontSize':'13px'})
    ], style=CARD)

    # ── Layout ────────────────────────────────────────────────────────────────
    return html.Div([
        kpi_row,

        # Row 1: top species + type donut
        html.Div([
            html.Div([stitle('Most Common in Storage'),
                      dcc.Graph(figure=fig_top, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
            html.Div([stitle('Type Distribution'),
                      dcc.Graph(figure=fig_donut, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),

        # Row 2: legendaries
        html.Div([
            html.Div([stitle('Legendaries in Storage', YELLOW),
                      dcc.Graph(figure=fig_leg, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),

        # Row 3: mythicals + medals
        html.Div([
            html.Div([stitle('Mythicals in Storage', PSYCHIC),
                      dcc.Graph(figure=fig_myth, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
            html.Div([stitle('Type Catch Medals'),
                      dcc.Graph(figure=fig_medals, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),

        # Row 3: items + rocket
        html.Div([
            html.Div([stitle('Key Item Inventory'),
                      dcc.Graph(figure=fig_items, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
            html.Div([
                rocket_cards,
                catch_table,
            ], style={'flex':'1','display':'flex','flexDirection':'column','gap':'0'}),
        ], style=ROW),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 3 — ENCOUNTERS
# ─────────────────────────────────────────────────────────────────────────────
def tab_encounters():
    enc = D['encounters']

    by_src = enc.groupby(['month','source']).size().reset_index(name='count')
    fig_src = go.Figure()
    for src, color in zip(['Map','Lure','Incense'],[ACCENT,WATER,GRASS]):
        df = by_src[by_src['source']==src]
        fig_src.add_trace(go.Bar(
            x=df['month'], y=df['count'], name=src,
            marker_color=color, opacity=0.85,
            hovertemplate=f'{src}: %{{x}}<br>%{{y:,}}<extra></extra>'
        ))
    fig_src.update_layout(**CHART, barmode='stack',
        title=dict(text='Encounters by Source — Map vs Lure vs Incense', font=dict(color=TEXT,size=13)),
        height=340)
    fig_src.update_xaxes(**AX, tickangle=45)
    fig_src.update_yaxes(**AX)

    by_hour = enc.groupby('hour').size().reset_index(name='count')
    fig_hr = go.Figure(go.Bar(
        x=by_hour['hour'], y=by_hour['count'],
        marker_color=[WATER if 6<=h<=20 else GHOST for h in by_hour['hour']],
        hovertemplate='%{x}:00h<br>%{y:,} encounters<extra></extra>',
    ))
    fig_hr.update_layout(**CHART,
        title=dict(text='Catch Activity by Hour of Day  (blue = daytime · purple = night)', font=dict(color=TEXT,size=13)),
        height=300, showlegend=False)
    fig_hr.update_xaxes(**AX, tickmode='linear', dtick=2)
    fig_hr.update_yaxes(**AX)

    city = enc[enc['city'].isin(['Boston','Mumbai'])].groupby('city').size().reset_index(name='count')
    fig_city = go.Figure(go.Pie(
        labels=city['city'], values=city['count'],
        hole=0.55,
        marker_colors=[WATER, FIRE],
        textfont=dict(family='Inter', color=WHITE, size=13),
        hovertemplate='%{label}<br>%{value:,} encounters (%{percent})<extra></extra>',
    ))
    fig_city.update_layout(**CHART,
        title=dict(text='Boston vs Mumbai', font=dict(color=TEXT,size=13)),
        height=300)

    by_yr = enc.groupby('year').size().reset_index(name='count')
    fig_yr = go.Figure(go.Bar(
        x=by_yr['year'].astype(str), y=by_yr['count'],
        marker_color=[BORDER if y!=2026 else ACCENT for y in by_yr['year']],
        text=by_yr['count'].apply(lambda v:f'{v:,}'),
        textposition='outside', textfont=dict(color=TEXT,size=11),
        hovertemplate='%{x}<br>%{y:,}<extra></extra>',
    ))
    fig_yr.update_layout(**CHART,
        title=dict(text='Encounters by Year — 2026 spike (+14,306!)', font=dict(color=TEXT,size=13)),
        height=300, showlegend=False)
    fig_yr.update_xaxes(**AX)
    fig_yr.update_yaxes(**AX)

    return html.Div([
        html.Div([stitle('Encounter Sources Over Time'),
                  dcc.Graph(figure=fig_src, config={'displayModeBar':False})], style=CARD),
        html.Div([
            html.Div([stitle('Hourly Activity'),
                      dcc.Graph(figure=fig_hr, config={'displayModeBar':False})],
                     style={**CARD,'flex':'2'}),
            html.Div([stitle('City Split'),
                      dcc.Graph(figure=fig_city, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),
        html.Div([stitle('Year Over Year'),
                  dcc.Graph(figure=fig_yr, config={'displayModeBar':False})], style=CARD),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 4 — LIVE MAP
# ─────────────────────────────────────────────────────────────────────────────
def tab_map():
    map_data = D['map_data']

    # Build Folium map
    m = folium.Map(
        location=[42.36, -71.06],
        zoom_start=12,
        tiles='CartoDB dark_matter',
    )

    type_config = {
        'Catch':      {'color':'#6366F1','radius':8},
        'Lure':       {'color':'#3B82F6','radius':10},
        'PokeStop':   {'color':'#10B981','radius':6},
        'Raid':       {'color':'#EF4444','radius':12},
        'Gym Deploy': {'color':'#F59E0B','radius':10},
    }

    for event_type, cfg in type_config.items():
        subset = map_data[map_data['type']==event_type].head(3000)
        if len(subset) == 0:
            continue
        heat_pts = list(zip(subset['lat'], subset['lon']))
        HeatMap(
            heat_pts,
            name=event_type,
            radius=cfg['radius'],
            blur=15,
            max_zoom=15,
            gradient={0.2:'#1a1d2e', 0.5:cfg['color']+'99', 1.0:cfg['color']},
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    title = '''<div style="position:fixed;top:16px;left:50%;transform:translateX(-50%);
        background:rgba(15,17,23,0.95);color:#F9FAFB;font-family:Inter,sans-serif;
        font-size:14px;font-weight:600;padding:10px 24px;border-radius:8px;
        border:1px solid #2A2D3E;z-index:9999;pointer-events:none;letter-spacing:1px;">
        APEXJBS · Boston Gameplay Map · 34,185 GPS Points
    </div>'''
    m.get_root().html.add_child(folium.Element(title))

    legend = '''<div style="position:fixed;bottom:30px;left:20px;
        background:rgba(15,17,23,0.95);color:#F9FAFB;font-family:Inter,sans-serif;
        font-size:12px;padding:14px 18px;border-radius:8px;
        border:1px solid #2A2D3E;z-index:9999;line-height:1.8;">
        <div style="font-weight:600;margin-bottom:6px;">Event Types</div>
        <div><span style="color:#6366F1">●</span> Catch (21,456)</div>
        <div><span style="color:#3B82F6">●</span> Lure (259)</div>
        <div><span style="color:#10B981">●</span> PokeStop (12,095)</div>
        <div><span style="color:#EF4444">●</span> Raid (375)</div>
        <div><span style="color:#F59E0B">●</span> Gym Deploy (344)</div>
    </div>'''
    m.get_root().html.add_child(folium.Element(legend))

    map_path = os.path.join('.', 'assets', 'pokemon_map.html')
    m.save(map_path)

    return html.Div([
        html.Div([
            html.Div([
                kpi('Total GPS Points', '34,185',  ACCENT),
                kpi('Catches',          '21,456',  GHOST),
                kpi('PokeStop Spins',   '12,095',  GRASS),
                kpi('Raids',            '375',     FIRE),
                kpi('Gym Deploys',      '344',     YELLOW),
                kpi('Lure Catches',     '259',     WATER),
            ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'}),
        ]),
        html.Div([
            html.Iframe(
                src='/assets/pokemon_map.html',
                style={'width':'100%','height':'620px','border':'none',
                       'borderRadius':'12px'}
            )
        ], style=CARD),
        html.Div([
            html.P('📍 All points filtered to Boston/Northeast area only. Mumbai data excluded.',
                   style={'color':MUTED,'fontFamily':'Inter','fontSize':'12px','margin':'0'}),
        ], style={'padding':'8px 0'}),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 5 — EXPLORATION
# ─────────────────────────────────────────────────────────────────────────────
def tab_exploration():
    ps_m = D['pokestops'].groupby('month').size().reset_index(name='spins')
    fig_ps = go.Figure(go.Bar(
        x=ps_m['month'], y=ps_m['spins'],
        marker_color=WATER, opacity=0.85,
        hovertemplate='%{x}<br>%{y:,} spins<extra></extra>',
    ))
    fig_ps.update_layout(**CHART,
        title=dict(text='Pokéstop Spins by Month', font=dict(color=TEXT,size=13)),
        height=300, showlegend=False)
    fig_ps.update_xaxes(**AX, tickangle=45)
    fig_ps.update_yaxes(**AX)

    b_m = D['battles'].groupby('month').size().reset_index(name='count'); b_m['type']='Battles'
    d_m = D['deploys'].groupby('month').size().reset_index(name='count'); d_m['type']='Deploys'
    f_m = D['feed'].groupby('month').size().reset_index(name='count');    f_m['type']='Berries Fed'
    fig_gym = go.Figure()
    for df, color in zip([b_m,d_m,f_m],[FIRE,GRASS,PSYCHIC]):
        fig_gym.add_trace(go.Scatter(
            x=df['month'], y=df['count'], name=df['type'].iloc[0],
            mode='lines+markers', line=dict(color=color,width=2),
            marker=dict(size=4),
            hovertemplate='%{x}<br>%{y:,}<extra></extra>'
        ))
    fig_gym.update_layout(**CHART,
        title=dict(text='Gym Activity — Battles vs Deploys vs Berries Fed', font=dict(color=TEXT,size=13)),
        height=300)
    fig_gym.update_xaxes(**AX, tickangle=45)
    fig_gym.update_yaxes(**AX)

    sess = D['sessions']['City'].value_counts().head(12).reset_index()
    sess.columns = ['city','count']
    fig_sess = go.Figure(go.Bar(
        x=sess['count'], y=sess['city'],
        orientation='h', marker_color=GHOST, opacity=0.85,
        text=sess['count'], textposition='outside',
        textfont=dict(color=TEXT,size=11),
        hovertemplate='%{y}<br>%{x:,} sessions<extra></extra>',
    ))
    fig_sess.update_layout(**CHART,
        title=dict(text='App Sessions by City', font=dict(color=TEXT,size=13)),
        height=400, showlegend=False)
    fig_sess.update_xaxes(**AX)
    fig_sess.update_yaxes(autorange='reversed', gridcolor=BORDER)

    ps_yr = D['pokestops'].groupby('year').size().reset_index(name='count')
    fig_psyr = go.Figure(go.Bar(
        x=ps_yr['year'].astype(str), y=ps_yr['count'],
        marker_color=[BORDER if y!=2026 else WATER for y in ps_yr['year']],
        text=ps_yr['count'].apply(lambda v:f'{v:,}'),
        textposition='outside', textfont=dict(color=TEXT,size=11),
        hovertemplate='%{x}<br>%{y:,} spins<extra></extra>',
    ))
    fig_psyr.update_layout(**CHART,
        title=dict(text='Pokéstop Spins by Year', font=dict(color=TEXT,size=13)),
        height=280, showlegend=False)
    fig_psyr.update_xaxes(**AX)
    fig_psyr.update_yaxes(**AX)

    return html.Div([
        html.Div([
            html.Div([stitle('Pokéstop Spins'),
                      dcc.Graph(figure=fig_ps,   config={'displayModeBar':False}),
                      dcc.Graph(figure=fig_psyr, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
            html.Div([stitle('Sessions by City'),
                      dcc.Graph(figure=fig_sess, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),
        html.Div([stitle('Gym Activity'),
                  dcc.Graph(figure=fig_gym, config={'displayModeBar':False})], style=CARD),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 6 — RAIDS
# ─────────────────────────────────────────────────────────────────────────────
def tab_raids():
    raids = D['raids']
    by_m = raids.groupby('month').size().reset_index(name='count')
    fig_m = go.Figure(go.Bar(
        x=by_m['month'], y=by_m['count'],
        marker_color=FIRE, opacity=0.85,
        hovertemplate='%{x}<br>%{y} raids<extra></extra>',
    ))
    fig_m.update_layout(**CHART,
        title=dict(text='Raids Joined by Month', font=dict(color=TEXT,size=13)),
        height=340, showlegend=False)
    fig_m.update_xaxes(**AX, tickangle=45)
    fig_m.update_yaxes(**AX)

    by_yr = raids.groupby('year').size().reset_index(name='count')
    fig_yr = go.Figure(go.Bar(
        x=by_yr['year'].astype(str), y=by_yr['count'],
        marker_color=[BORDER if y!=2026 else FIRE for y in by_yr['year']],
        text=by_yr['count'], textposition='outside',
        textfont=dict(color=TEXT,size=11),
        hovertemplate='%{x}<br>%{y} raids<extra></extra>',
    ))
    fig_yr.update_layout(**CHART,
        title=dict(text='Raids by Year', font=dict(color=TEXT,size=13)),
        height=300, showlegend=False)
    fig_yr.update_xaxes(**AX)
    fig_yr.update_yaxes(**AX)

    by_hr = raids.groupby('hour').size().reset_index(name='count')
    fig_hr = go.Figure(go.Bar(
        x=by_hr['hour'], y=by_hr['count'],
        marker_color=PSYCHIC,
        hovertemplate='%{x}:00h<br>%{y} raids<extra></extra>',
    ))
    fig_hr.update_layout(**CHART,
        title=dict(text='Raid Time by Hour', font=dict(color=TEXT,size=13)),
        height=300, showlegend=False)
    fig_hr.update_xaxes(**AX, tickmode='linear', dtick=2)
    fig_hr.update_yaxes(**AX)

    return html.Div([
        html.Div([
            kpi('Total Raids',  str(len(raids)),  FIRE),
            kpi('Peak Year',    '2026 (196)',      ACCENT),
            kpi('Peak Month',   'Apr 2026',        YELLOW),
            kpi('Night Raids',  f"{len(raids[raids['hour'].isin(range(20,24))|raids['hour'].isin(range(0,6))]):,}", GHOST),
        ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'}),
        html.Div([stitle('Raid Activity by Month'),
                  dcc.Graph(figure=fig_m, config={'displayModeBar':False})], style=CARD),
        html.Div([
            html.Div([stitle('By Year'),
                      dcc.Graph(figure=fig_yr, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
            html.Div([stitle('By Hour'),
                      dcc.Graph(figure=fig_hr, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 7 — FITNESS
# ─────────────────────────────────────────────────────────────────────────────
def tab_fitness():
    fit = D['fitness']
    avg = fit['Steps walked'].mean()

    fig_s = go.Figure()
    fig_s.add_trace(go.Bar(
        x=fit['date'], y=fit['Steps walked'],
        marker_color=[GRASS if v>=avg else ACCENT for v in fit['Steps walked']],
        hovertemplate='%{x}<br>%{y:,} steps<extra></extra>',
        name='Steps'
    ))
    fig_s.add_hline(y=avg, line_dash='dash', line_color=FIRE,
        annotation_text=f'avg {avg:,.0f}', annotation_font_color=FIRE)
    fig_s.update_layout(**CHART,
        title=dict(text='Daily Steps — green = above average', font=dict(color=TEXT,size=13)),
        height=320, showlegend=False)
    fig_s.update_xaxes(**AX, tickangle=45)
    fig_s.update_yaxes(**AX)

    fig_d = go.Figure(go.Scatter(
        x=fit['date'], y=fit['km'],
        mode='lines+markers', line=dict(color=WATER,width=2.5),
        marker=dict(size=5), fill='tozeroy',
        fillcolor='rgba(59,130,246,0.1)',
        hovertemplate='%{x}<br>%{y:.2f} km<extra></extra>',
    ))
    fig_d.update_layout(**CHART,
        title=dict(text='Daily Distance (km)', font=dict(color=TEXT,size=13)),
        height=280, showlegend=False)
    fig_d.update_xaxes(**AX, tickangle=45)
    fig_d.update_yaxes(**AX)

    fig_c = go.Figure(go.Bar(
        x=fit['date'], y=fit['Calories burned'],
        marker_color=FIRE, opacity=0.85,
        hovertemplate='%{x}<br>%{y} kcal<extra></extra>',
    ))
    fig_c.update_layout(**CHART,
        title=dict(text='Calories Burned', font=dict(color=TEXT,size=13)),
        height=280, showlegend=False)
    fig_c.update_xaxes(**AX, tickangle=45)
    fig_c.update_yaxes(**AX)

    return html.Div([
        html.Div([
            kpi('Steps (3wk)',  f"{fit['Steps walked'].sum():,}",    ACCENT),
            kpi('Distance',     f"{fit['km'].sum():.1f} km",         WATER),
            kpi('Calories',     f"{fit['Calories burned'].sum():,}", FIRE),
            kpi('Active Days',  str(len(fit)),                        GRASS),
            kpi('Lifetime km',  '5,600.6 km',                        YELLOW, 'Total walked'),
        ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'}),
        html.Div([stitle('Daily Steps'),
                  dcc.Graph(figure=fig_s, config={'displayModeBar':False})], style=CARD),
        html.Div([
            html.Div([stitle('Distance'),
                      dcc.Graph(figure=fig_d, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
            html.Div([stitle('Calories'),
                      dcc.Graph(figure=fig_c, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 8 — SPENDING
# ─────────────────────────────────────────────────────────────────────────────
def tab_spending():
    by_yr = D['coins_by_year']
    fig_yr = go.Figure(go.Bar(
        x=by_yr['year'].astype(str), y=by_yr['coins'],
        marker_color=[PSYCHIC if y==2023 else BORDER for y in by_yr['year']],
        text=by_yr['coins'].apply(lambda v:f'{int(v):,}'),
        textposition='outside', textfont=dict(color=TEXT,size=11),
        hovertemplate='%{x}<br>%{y:,} coins<extra></extra>',
    ))
    fig_yr.update_layout(**CHART,
        title=dict(text='PokéCoin Spending by Year — Peak 2023', font=dict(color=TEXT,size=13)),
        height=350, showlegend=False)
    fig_yr.update_xaxes(**AX)
    fig_yr.update_yaxes(**AX)

    items = D['top_items']
    fig_it = go.Figure(go.Bar(
        x=items['count'], y=items['label'],
        orientation='h', marker_color=YELLOW, opacity=0.85,
        text=items['count'], textposition='outside',
        textfont=dict(color=TEXT,size=11),
        hovertemplate='%{y}<br>%{x:,} times<extra></extra>',
    ))
    fig_it.update_layout(**CHART,
        title=dict(text='Top Items Acquired', font=dict(color=TEXT,size=13)),
        height=380, showlegend=False)
    fig_it.update_xaxes(**AX)
    fig_it.update_yaxes(autorange='reversed', gridcolor=BORDER)

    return html.Div([
        html.Div([
            kpi('Total Spent',    f"{int(by_yr['coins'].sum()):,} coins", PSYCHIC),
            kpi('Peak Year',      '2023 — 8,039 coins',                   FIRE),
            kpi('Current Balance','401 coins',                             YELLOW),
            kpi('Transactions',   f"{len(D['iap']):,}",                   GHOST),
        ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'}),
        html.Div([
            html.Div([stitle('Spending by Year'),
                      dcc.Graph(figure=fig_yr, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
            html.Div([stitle('Top Items'),
                      dcc.Graph(figure=fig_it, config={'displayModeBar':False})],
                     style={**CARD,'flex':'1'}),
        ], style=ROW),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 9 — SOCIAL
# ─────────────────────────────────────────────────────────────────────────────
def tab_social():
    by_yr = D['friends_by_year']
    fig_g = go.Figure(go.Scatter(
        x=by_yr['year'], y=by_yr['cumulative'],
        mode='lines+markers+text',
        line=dict(color=PSYCHIC,width=3),
        marker=dict(size=10,color=BG,line=dict(color=PSYCHIC,width=2.5)),
        fill='tozeroy', fillcolor='rgba(236,72,153,0.07)',
        text=by_yr['cumulative'], textposition='top center',
        textfont=dict(color=PSYCHIC,size=11),
        hovertemplate='%{x}<br>%{y} total friends<extra></extra>',
    ))
    fig_g.update_layout(**CHART,
        title=dict(text='Cumulative Friend Count', font=dict(color=TEXT,size=13)),
        height=300)
    fig_g.update_xaxes(**AX)
    fig_g.update_yaxes(**AX)

    fig_n = go.Figure(go.Bar(
        x=by_yr['year'].astype(str), y=by_yr['new_friends'],
        marker_color=PSYCHIC, opacity=0.85,
        text=by_yr['new_friends'].apply(lambda v:f'+{v}'),
        textposition='outside', textfont=dict(color=PSYCHIC,size=12),
        hovertemplate='%{x}<br>+%{y} new friends<extra></extra>',
    ))
    fig_n.update_layout(**CHART,
        title=dict(text='New Friends Added per Year', font=dict(color=TEXT,size=13)),
        height=300, showlegend=False)
    fig_n.update_xaxes(**AX)
    fig_n.update_yaxes(**AX)

    unf = D['unfriended']
    unf_rows = [
        html.Tr([
            html.Td(r['Name of unfriended friend'],
                    style={'color':TEXT,'padding':'8px 12px','fontWeight':'500'}),
            html.Td(str(r['dt'])[:10],
                    style={'color':MUTED,'padding':'8px 12px','fontSize':'11px'}),
        ], style={'borderBottom':f'1px solid {BORDER}'})
        for _, r in unf.iterrows()
    ]

    return html.Div([
        html.Div([
            kpi('Total Friends', str(len(D['friends'])), PSYCHIC),
            kpi('Unfriended',    '14',                    FIRE),
            kpi('Best Year',     '2026 — +50',           YELLOW),
            kpi('Started',       '2021',                  MUTED),
        ], style={'display':'flex','gap':'10px','flexWrap':'wrap','marginBottom':'16px'}),
        html.Div([
            html.Div([
                stitle('Friend Growth'),
                dcc.Graph(figure=fig_g, config={'displayModeBar':False}),
                html.Div([
                    stitle('New per Year'),
                    dcc.Graph(figure=fig_n, config={'displayModeBar':False}),
                ], style={**CARD,'marginTop':'16px'}),
            ], style={'flex':'2'}),
            html.Div([
                html.Div([
                    stitle('Recently Unfriended (14)', FIRE),
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th('Player', style={'color':MUTED,'padding':'8px 12px',
                                'fontSize':'11px','fontWeight':'600','textTransform':'uppercase'}),
                            html.Th('Date',   style={'color':MUTED,'padding':'8px 12px',
                                'fontSize':'11px','fontWeight':'600','textTransform':'uppercase'}),
                        ], style={'borderBottom':f'2px solid {BORDER}'})),
                        html.Tbody(unf_rows),
                    ], style={'width':'100%','borderCollapse':'collapse',
                              'fontFamily':'Inter','fontSize':'13px'})
                ], style=CARD),
            ], style={'flex':'1'}),
        ], style=ROW),
    ])

# ─────────────────────────────────────────────────────────────────────────────
#  LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
app.layout = html.Div([

    # Header
    html.Div([
        html.Div([
            html.Div('Pokemon GO', style={
                'fontSize':'26px','fontWeight':'700','color':WHITE,
                'fontFamily':'Inter, sans-serif','letterSpacing':'-0.5px',
            }),
            html.Div('Player Insights  ·  APEXJBS  ·  2016 – 2026', style={
                'fontSize':'12px','color':MUTED,'fontFamily':'Inter, sans-serif',
                'marginTop':'3px','letterSpacing':'0.04em',
            }),
        ]),
        html.Div([
            html.Span('LVL 61 ', style={'color':YELLOW,'fontWeight':'700',
                'fontFamily':'Inter','fontSize':'18px'}),
            html.Span('· 38,100,947 XP · 5,600 km walked', style={
                'color':MUTED,'fontFamily':'Inter','fontSize':'12px'}),
        ]),
    ], style={
        'background': PANEL,'borderBottom':f'1px solid {BORDER}',
        'padding':'18px 32px','display':'flex',
        'justifyContent':'space-between','alignItems':'center',
    }),

    # Tabs
    html.Div([
        dcc.Tabs(id='tabs', value='overview',
            style={'borderBottom':f'1px solid {BORDER}'},
            children=[
                dcc.Tab(label='Overview',    value='overview',    style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Pokemon',     value='pokemon',     style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Encounters',  value='encounters',  style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Live Map',    value='map',         style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Exploration', value='exploration', style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Raids',       value='raids',       style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Fitness',     value='fitness',     style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Spending',    value='spending',    style=TAB_S, selected_style=TAB_SEL),
                dcc.Tab(label='Social',      value='social',      style=TAB_S, selected_style=TAB_SEL),
            ]
        ),
        html.Div(id='tab-content', style={'padding':'24px 32px'}),
    ]),

], style={'backgroundColor':BG,'minHeight':'100vh',
          'fontFamily':'Inter, system-ui, sans-serif'})


@app.callback(Output('tab-content','children'), Input('tabs','value'))
def render(tab):
    if tab == 'overview':    return tab_overview()
    if tab == 'pokemon':     return tab_pokemon()
    if tab == 'encounters':  return tab_encounters()
    if tab == 'map':         return tab_map()
    if tab == 'exploration': return tab_exploration()
    if tab == 'raids':       return tab_raids()
    if tab == 'fitness':     return tab_fitness()
    if tab == 'spending':    return tab_spending()
    if tab == 'social':      return tab_social()


if __name__ == '__main__':
    app.run(debug=True)