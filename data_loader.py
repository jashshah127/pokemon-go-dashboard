# data_loader.py
import os, re, zipfile
import pandas as pd
from collections import Counter

DATA_DIR    = "."
JOURNEY_DIR = os.path.join(DATA_DIR, "player_journey_extracted")

# ── Type map ──────────────────────────────────────────────────────────────────
POKEMON_TYPES = {
    # Normal
    'Bibarel':'Normal','Blissey':'Normal','Bouffalant':'Normal','Braviary':'Normal',
    'Buneary':'Normal','Chansey':'Normal','Clefable':'Normal','Clefairy':'Normal',
    'Cleffa':'Normal','Deerling':'Normal','Delcatty':'Normal','Dodrio':'Normal',
    'Doduo':'Normal','Dubwool':'Normal','Dudunsparce':'Normal','Eevee':'Normal',
    "Farfetch'D":'Normal','Fearow':'Normal','Furret':'Normal','Girafarig':'Normal',
    'Greedent':'Normal','Gumshoos':'Normal','Herdier':'Normal','Igglybuff':'Normal',
    'Indeedee':'Normal','Jigglypuff':'Normal','Komala':'Normal','Lechonk':'Normal',
    'Lickilicky':'Normal','Lickitung':'Normal','Lopunny':'Normal','Meowth':'Normal',
    'Miltank':'Normal','Minun':'Normal','Mr. Mime':'Normal','Munchlax':'Normal',
    'Noctowl':'Normal','Oinkologne':'Normal','Pidgeot':'Normal','Pidgey':'Normal',
    'Pidove':'Normal','Plusle':'Normal','Porygon':'Normal','Porygon Z':'Normal',
    'Purugly':'Normal','Raticate':'Normal','Rattata':'Normal','Sentret':'Normal',
    'Slaking':'Normal','Smeargle':'Normal','Snorlax':'Normal','Stantler':'Normal',
    'Staraptor':'Normal','Staravia':'Normal','Starly':'Normal','Stoutland':'Normal',
    'Tandemaus':'Normal','Tauros':'Normal','Togepi':'Normal','Togetic':'Normal',
    'Ursaluna':'Normal','Wigglytuff':'Normal','Wooloo':'Normal','Yungoos':'Normal',
    'Zangoose':'Normal','Zigzagoon':'Normal',
    # Fire
    'Arcanine':'Fire','Armarouge':'Fire','Blaziken':'Fire','Camerupt':'Fire',
    'Centiskorch':'Fire','Charcadet':'Fire','Charizard':'Fire','Charmander':'Fire',
    'Cinderace':'Fire','Combusken':'Fire','Darumaka':'Fire','Delphox':'Fire',
    'Fennekin':'Fire','Fletchinder':'Fire','Flareon':'Fire','Fuecoco':'Fire',
    'Growlithe':'Fire','Heatmor':'Fire','Ho-Oh':'Fire','Incineroar':'Fire',
    'Infernape':'Fire','Litten':'Fire','Litleo':'Fire','Litwick':'Fire',
    'Magmar':'Fire','Magmortar':'Fire','Monferno':'Fire','Moltres':'Fire',
    'Ninetales':'Fire','Numel':'Fire','Pansear':'Fire','Ponyta':'Fire',
    'Pyroar':'Fire','Raboot':'Fire','Rapidash':'Fire','Salandit':'Fire',
    'Scorbunny':'Fire','Simisear':'Fire','Skeledirge':'Fire','Talonflame':'Fire',
    'Torkoal':'Fire','Turtonator':'Fire','Typhlosion':'Fire','Volcanion':'Fire',
    # Water
    'Barboach':'Water','Basculin':'Water','Beartic':'Water','Blastoise':'Water',
    'Buizel':'Water','Carracosta':'Water','Cetitan':'Water','Clawitzer':'Water',
    'Clamperl':'Water','Cloyster':'Water','Corsola':'Water','Crabrawler':'Water',
    'Crawdaunt':'Water','Dewgong':'Water','Dewpider':'Water','Feebas':'Water',
    'Finneon':'Water','Frillish':'Water','Froakie':'Water','Gastrodon':'Water',
    'Gorebyss':'Water','Greninja':'Water','Gyarados':'Water','Horsea':'Water',
    'Jellicent':'Water','Kabuto':'Water','Kingdra':'Water','Kingler':'Water',
    'Krabby':'Water','Kyogre':'Water','Lapras':'Water','Lumineon':'Water',
    'Magikarp':'Water','Marill':'Water','Mantyke':'Water','Milotic':'Water',
    'Mudkip':'Water','Octillery':'Water','Oshawott':'Water','Panpour':'Water',
    'Popplio':'Water','Poliwag':'Water','Poliwhirl':'Water','Poliwrath':'Water',
    'Primarina':'Water','Psyduck':'Water','Quagsire':'Water','Quaxly':'Water',
    'Qwilfish':'Water','Remoraid':'Water','Samurott':'Water','Seadra':'Water',
    'Seaking':'Water','Sealeo':'Water','Seismitoad':'Water','Shellder':'Water',
    'Shellos':'Water','Slowbro':'Water','Slowking':'Water','Slowpoke':'Water',
    'Squirtle':'Water','Staryu':'Water','Starmie':'Water','Swampert':'Water',
    'Swanna':'Water','Tentacruel':'Water','Tirtouga':'Water','Totodile':'Water',
    'Tympole':'Water','Vaporeon':'Water','Wailord':'Water','Walrein':'Water',
    'Wartortle':'Water','Whiscash':'Water',
    # Grass
    'Arboliva':'Grass','Bellossom':'Grass','Bellsprout':'Grass','Bounsweet':'Grass',
    'Breloom':'Grass','Bulbasaur':'Grass','Cacnea':'Grass','Cacturne':'Grass',
    'Cherubi':'Grass','Chespin':'Grass','Chikorita':'Grass','Cottonee':'Grass',
    'Decidueye':'Grass','Eldegoss':'Grass','Fomantis':'Grass','Foongus':'Grass',
    'Grotle':'Grass','Grovyle':'Grass','Grookey':'Grass','Jumpluff':'Grass',
    'Leafeon':'Grass','Leavanny':'Grass','Lilligant':'Grass','Meganium':'Grass',
    'Morelull':'Grass','Nuzleaf':'Grass','Petilil':'Grass','Rillaboom':'Grass',
    'Roselia':'Grass','Rowlet':'Grass','Sceptile':'Grass','Sewaddle':'Grass',
    'Shiftry':'Grass','Shiinotic':'Grass','Simisage':'Grass','Skiddo':'Grass',
    'Smoliv':'Grass','Sprigatito':'Grass','Sunkern':'Grass','Tangrowth':'Grass',
    'Treecko':'Grass','Turtwig':'Grass','Venipede':'Grass','Venusaur':'Grass',
    'Whimsicott':'Grass',
    # Electric
    'Ampharos':'Electric','Bellibolt':'Electric','Blitzle':'Electric',
    'Dedenne':'Electric','Electivire':'Electric','Eelektrik':'Electric',
    'Electrode':'Electric','Emolga':'Electric','Galvantula':'Electric',
    'Jolteon':'Electric','Joltik':'Electric','Luxio':'Electric','Luxray':'Electric',
    'Magneton':'Electric','Magnezone':'Electric','Morpeko':'Electric',
    'Pawmo':'Electric','Pichu':'Electric','Pikachu':'Electric',
    'Raichu':'Electric','Revavroom':'Electric','Shinx':'Electric',
    'Stunfisk':'Electric','Tapu Koko':'Electric','Tadbulb':'Electric',
    'Togedemaru':'Electric','Varoom':'Electric','Vikavolt':'Electric',
    'Voltorb':'Electric','Zebstrika':'Electric',
    # Psychic
    'Abra':'Psychic','Audino':'Psychic','Azelf':'Psychic','Celebi':'Psychic',
    'Chimecho':'Psychic','Chingling':'Psychic','Cosmog':'Psychic',
    'Cresselia':'Psychic','Drowzee':'Psychic','Enamorus':'Psychic',
    'Espeon':'Psychic','Exeggcute':'Psychic','Exeggutor':'Psychic',
    'Gardevoir':'Psychic','Gothita':'Psychic','Hatenna':'Psychic',
    'Hatterene':'Psychic','Hypno':'Psychic','Jirachi':'Psychic','Jynx':'Psychic',
    'Latias':'Psychic','Latios':'Psychic','Mewtwo':'Psychic','Mesprit':'Psychic',
    'Metang':'Psychic','Metagross':'Psychic','Musharna':'Psychic','Munna':'Psychic',
    'Necrozma':'Psychic','Natu':'Psychic','Ralts':'Psychic','Slowbro':'Psychic',
    'Slowking':'Psychic','Slowpoke':'Psychic','Smoochum':'Psychic',
    'Solrock':'Psychic','Spoink':'Psychic','Starmie':'Psychic','Swoobat':'Psychic',
    'Uxie':'Psychic','Victini':'Psychic','Wobbuffet':'Psychic','Woobat':'Psychic',
    'Xatu':'Psychic',
    # Dark
    'Absol':'Dark','Bisharp':'Dark','Darkrai':'Dark','Drapion':'Dark',
    'Greninja':'Dark','Houndoom':'Dark','Hydreigon':'Dark','Honchkrow':'Dark',
    'Inkay':'Dark','Liepard':'Dark','Mightyena':'Dark','Morgrem':'Dark',
    'Murkrow':'Dark','Obstagoon':'Dark','Pawniard':'Dark','Sableye':'Dark',
    'Scrafty':'Dark','Scraggy':'Dark','Shiftry':'Dark','Skuntank':'Dark',
    'Sneasel':'Dark','Stunky':'Dark','Thievul':'Dark','Tyranitar':'Dark',
    'Umbreon':'Dark','Weavile':'Dark',
    # Fighting
    'Annihilape':'Fighting','Bewear':'Fighting','Breloom':'Fighting',
    'Buzzwole':'Fighting','Cobalion':'Fighting','Crabrawler':'Fighting',
    'Falinks':'Fighting','Hariyama':'Fighting','Heracross':'Fighting',
    'Hitmonchan':'Fighting','Hitmonlee':'Fighting','Hitmontop':'Fighting',
    'Infernape':'Fighting','Kubfu':'Fighting','Machamp':'Fighting',
    'Machoke':'Fighting','Machop':'Fighting','Makuhita':'Fighting',
    'Mankey':'Fighting','Mienshao':'Fighting','Pancham':'Fighting',
    'Pheromosa':'Fighting','Poliwrath':'Fighting','Primeape':'Fighting',
    'Sawk':'Fighting','Sirfetchd':'Fighting','Terrakion':'Fighting',
    'Throh':'Fighting','Timburr':'Fighting','Toxicroak':'Fighting',
    # Dragon
    'Axew':'Dragon','Bagon':'Dragon','Deino':'Dragon','Dialga':'Dragon',
    'Dratini':'Dragon','Dragonite':'Dragon','Dragalge':'Dragon',
    'Druddigon':'Dragon','Flygon':'Dragon','Frigibax':'Dragon',
    'Garchomp':'Dragon','Gible':'Dragon','Giratina':'Dragon','Goodra':'Dragon',
    'Jangmo O':'Dragon','Kingdra':'Dragon','Kyurem':'Dragon','Noibat':'Dragon',
    'Palkia':'Dragon','Rayquaza':'Dragon','Salamence':'Dragon','Shelgon':'Dragon',
    'Turtonator':'Dragon','Tyrunt':'Dragon','Tyrantrum':'Dragon',
    # Ghost
    'Chandelure':'Ghost','Cofagrigus':'Ghost','Drifblim':'Ghost',
    'Drifloon':'Ghost','Dusknoir':'Ghost','Duskull':'Ghost','Gastly':'Ghost',
    'Gengar':'Ghost','Golurk':'Ghost','Gourgeist':'Ghost','Greavard':'Ghost',
    'Honedge':'Ghost','Jellicent':'Ghost','Litwick':'Ghost','Mimikyu':'Ghost',
    'Misdreavus':'Ghost','Mismagius':'Ghost','Phantump':'Ghost',
    'Pumpkaboo':'Ghost','Shuppet':'Ghost','Sinistea':'Ghost',
    'Trevenant':'Ghost','Yamask':'Ghost',
    # Rock
    'Aerodactyl':'Rock','Amaura':'Rock','Archen':'Rock','Archeops':'Rock',
    'Binacle':'Rock','Boldore':'Rock','Carbink':'Rock','Carracosta':'Rock',
    'Cranidos':'Rock','Dwebble':'Rock','Gigalith':'Rock','Lunatone':'Rock',
    'Nosepass':'Rock','Omastar':'Rock','Rampardos':'Rock','Regirock':'Rock',
    'Rhyhorn':'Rock','Rhydon':'Rock','Rhyperior':'Rock','Rockruff':'Rock',
    'Roggenrola':'Rock','Shieldon':'Rock','Sudowoodo':'Rock',
    # Ground
    'Baltoy':'Ground','Diggersby':'Ground','Diglett':'Ground','Dugtrio':'Ground',
    'Excadrill':'Ground','Garchomp':'Ground','Gastrodon':'Ground',
    'Gible':'Ground','Gliscor':'Ground','Golurk':'Ground','Hippowdon':'Ground',
    'Landorus':'Ground','Mamoswine':'Ground','Nidoking':'Ground',
    'Nidoqueen':'Ground','Nidoran':'Ground','Nidorina':'Ground',
    'Nidorino':'Ground','Numel':'Ground','Onix':'Ground','Rhyhorn':'Ground',
    'Rhydon':'Ground','Rhyperior':'Ground','Sandshrew':'Ground',
    'Sandslash':'Ground','Sandygast':'Ground','Seismitoad':'Ground',
    'Stunfisk':'Ground','Swampert':'Ground','Trapinch':'Ground',
    'Whiscash':'Ground','Wooper':'Ground',
    # Ice
    'Articuno':'Ice','Beartic':'Ice','Cetitan':'Ice','Cloyster':'Ice',
    'Delibird':'Ice','Dewgong':'Ice','Frigibax':'Ice','Jynx':'Ice',
    'Lapras':'Ice','Mamoswine':'Ice','Regice':'Ice','Sealeo':'Ice',
    'Smoochum':'Ice','Snorunt':'Ice','Snover':'Ice','Swinub':'Ice',
    'Walrein':'Ice','Weavile':'Ice',
    # Bug
    'Beautifly':'Bug','Burmy':'Bug','Butterfree':'Bug','Caterpie':'Bug',
    'Combee':'Bug','Cutiefly':'Bug','Dewpider':'Bug','Dwebble':'Bug',
    'Galvantula':'Bug','Genesect':'Bug','Heracross':'Bug','Joltik':'Bug',
    'Karrablast':'Bug','Kricketot':'Bug','Kricketune':'Bug','Larvesta':'Bug',
    'Ledian':'Bug','Ledyba':'Bug','Leavanny':'Bug','Masquerain':'Bug',
    'Nymble':'Bug','Pheromosa':'Bug','Pinsir':'Bug','Scatterbug':'Bug',
    'Sewaddle':'Bug','Shelmet':'Bug','Venipede':'Bug','Vikavolt':'Bug',
    'Vivillon':'Bug','Whirlipede':'Bug','Yanma':'Bug','Yanmega':'Bug',
    # Poison
    'Amoonguss':'Poison','Crobat':'Poison','Croagunk':'Poison',
    'Dragalge':'Poison','Ekans':'Poison','Foongus':'Poison','Golbat':'Poison',
    'Grimer':'Poison','Gulpin':'Poison','Koffing':'Poison','Muk':'Poison',
    'Nihilego':'Poison','Qwilfish':'Poison','Salandit':'Poison',
    'Seviper':'Poison','Shroodle':'Poison','Skuntank':'Poison',
    'Stunky':'Poison','Swalot':'Poison','Tentacruel':'Poison',
    'Toxapex':'Poison','Toxel':'Poison','Toxicroak':'Poison',
    'Venonat':'Poison','Weezing':'Poison','Zubat':'Poison',
    # Steel
    'Aggron':'Steel','Beldum':'Steel','Bisharp':'Steel','Cobalion':'Steel',
    'Dialga':'Steel','Empoleon':'Steel','Excadrill':'Steel','Falinks':'Steel',
    'Ferroseed':'Steel','Genesect':'Steel','Gigalith':'Steel','Honedge':'Steel',
    'Jirachi':'Steel','Kleavor':'Steel','Klefki':'Steel','Klink':'Steel',
    'Magneton':'Steel','Magnezone':'Steel','Mawile':'Steel','Metagross':'Steel',
    'Metang':'Steel','Pawniard':'Steel','Perrserker':'Steel','Registeel':'Steel',
    'Skarmory':'Steel','Steelix':'Steel','Stakataka':'Steel',
    'Tinkatink':'Steel','Tinkaton':'Steel','Zacian':'Steel',
    # Fairy
    'Aromatisse':'Fairy','Carbink':'Fairy','Clefable':'Fairy','Clefairy':'Fairy',
    'Cleffa':'Fairy','Cottonee':'Fairy','Cutiefly':'Fairy','Dedenne':'Fairy',
    'Enamorus':'Fairy','Fidough':'Fairy','Flabebe':'Fairy','Gardevoir':'Fairy',
    'Granbull':'Fairy','Hatenna':'Fairy','Hatterene':'Fairy','Igglybuff':'Fairy',
    'Jigglypuff':'Fairy','Klefki':'Fairy','Marill':'Fairy','Mawile':'Fairy',
    'Mimikyu':'Fairy','Ribombee':'Fairy','Slurpuff':'Fairy','Snubbull':'Fairy',
    'Swirlix':'Fairy','Tapu Bulu':'Fairy','Tapu Fini':'Fairy',
    'Tapu Koko':'Fairy','Tinkatink':'Fairy','Tinkaton':'Fairy',
    'Togepi':'Fairy','Togetic':'Fairy','Whimsicott':'Fairy',
    'Wigglytuff':'Fairy','Xerneas':'Fairy',
    # Flying
    'Aerodactyl':'Flying','Articuno':'Flying','Braviary':'Flying',
    'Dodrio':'Flying','Doduo':'Flying','Dragonite':'Flying','Drifblim':'Flying',
    'Drifloon':'Flying','Emolga':'Flying','Fearow':'Flying','Flamigo':'Flying',
    'Fletchinder':'Flying','Gyarados':'Flying','Ho-Oh':'Flying',
    'Honchkrow':'Flying','Hoothoot':'Flying','Jumpluff':'Flying',
    'Landorus':'Flying','Moltres':'Flying','Murkrow':'Flying',
    'Noctowl':'Flying','Noibat':'Flying','Oricorio':'Flying','Pidgeot':'Flying',
    'Pidgey':'Flying','Pidove':'Flying','Rayquaza':'Flying','Rookidee':'Flying',
    'Skarmory':'Flying','Staraptor':'Flying','Staravia':'Flying',
    'Starly':'Flying','Swablu':'Flying','Swanna':'Flying','Swellow':'Flying',
    'Taillow':'Flying','Talonflame':'Flying','Thundurus':'Flying',
    'Tornadus':'Flying','Toucannon':'Flying','Vivillon':'Flying',
    'Yanma':'Flying','Yanmega':'Flying','Zubat':'Flying',
}

TYPE_COLORS = {
    'Fire':'#FF6B35','Water':'#00B4FF','Grass':'#39FF14','Electric':'#F7FF00',
    'Psychic':'#FF3CAC','Dark':'#9B59FF','Fighting':'#FF8C42','Dragon':'#6A5ACD',
    'Ghost':'#7B68EE','Rock':'#C8A96E','Ground':'#DEB887','Ice':'#87CEEB',
    'Bug':'#90EE90','Poison':'#DA70D6','Steel':'#A9A9A9','Fairy':'#FFB6C1',
    'Flying':'#87CEFA','Normal':'#D3D3D3',
}

def extract_journey():
    zip_path = os.path.join(DATA_DIR, "Player_Journey.zip")
    if not os.path.exists(JOURNEY_DIR):
        os.makedirs(JOURNEY_DIR)
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(JOURNEY_DIR)

def load_tsv(f):
    return pd.read_csv(os.path.join(DATA_DIR, f), sep='\t')

def load_csv(f):
    return pd.read_csv(os.path.join(JOURNEY_DIR, f))

def parse_ts(df, col='Timestamp'):
    df['ts'] = pd.to_datetime(df[col], format='mixed', utc=True)
    return df

def clean_name(raw):
    n = re.sub(r'V\d+_POKEMON_', '', raw)
    n = n.replace('_', ' ').split('(')[0].strip().title()
    return n

def boston_filter(df):
    return df[
        (df['Player_Latitude']  > 41) & (df['Player_Latitude']  < 43) &
        (df['Player_Longitude'] > -73) & (df['Player_Longitude'] < -70)
    ]

# ─────────────────────────────────────────────────────────────────────────────
def load_gameplay():
    with open(os.path.join(DATA_DIR, 'Gameplay.txt'), 'r') as f:
        text = f.read()

    stats = {
        'level':       int(re.search(r'Level: (\d+)', text).group(1)),
        'xp':          int(re.search(r'Total XP: (\d+)', text).group(1)),
        'distance_km': float(re.search(r'Distance walked: ([\d.]+)', text).group(1)),
        'stardust':    int(re.search(r'Stardust: (\d+)', text).group(1)),
        'pokecoins':   int(re.search(r'Pokecoin: (\d+)', text).group(1)),
        'eggs_hatched':int(re.search(r'You have hatched (\d+)', text).group(1)),
        'start_date':  re.search(r'Start date: (.+)', text).group(1).strip(),
        'buddy':       clean_name(re.search(r'Buddy nickname: (.+)', text).group(1).strip()),
    }

    # Collection
    coll_raw = re.search(r'Pokemon in your collection:\n(.*?)\nYou have hatched', text, re.DOTALL)
    collection, types_list = [], []
    for line in coll_raw.group(1).strip().split('\n'):
        raw = line.strip().replace('\t','')
        if raw:
            name = clean_name(raw)
            collection.append(name)
            types_list.append(POKEMON_TYPES.get(name, 'Other'))

    stats['total_pokemon']  = len(collection)
    stats['unique_species'] = len(set(collection))

    collection_df = pd.DataFrame(
        Counter(collection).most_common(), columns=['pokemon','count']
    )

    type_df = pd.DataFrame(
        Counter(types_list).most_common(), columns=['type','count']
    )
    type_df = type_df[type_df['type'] != 'Other']
    type_df['color'] = type_df['type'].map(TYPE_COLORS).fillna('#888')

    # Items
    items_raw = re.search(r'You have \d+ items:\n(.*?)\nYou have \d+ medals', text, re.DOTALL)
    item_name_map = {
        'ITEM_EVENT_PASS_POINT_MONTHLY_01':'Monthly Pass Pts (1)',
        'ITEM_EVENT_PASS_POINT_MONTHLY_02':'Monthly Pass Pts (2)',
        'ITEM_EVENT_PASS_POINT_MONTHLY_03':'Monthly Pass Pts (3)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_01':'Live Ops Pts (1)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_02':'Live Ops Pts (2)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_03':'Live Ops Pts (3)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_04':'Live Ops Pts (4)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_05':'Live Ops Pts (5)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_06':'Live Ops Pts (6)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_07':'Live Ops Pts (7)',
        'ITEM_EVENT_PASS_POINT_LIVE_OPS_08':'Live Ops Pts (8)',
        'ITEM_EVENT_PASS_POINT_GO_TOUR_01':'GO Tour Points',
        'ITEM_MP':'Mega Points','ITEM_ENHANCED_CURRENCY':'Premium Currency',
        'ITEM_REMOTE_RAID_TICKET':'Remote Raid Pass',
        'ITEM_INCENSE_DAILY_ADVENTURE':'Adventure Incense',
        'ITEM_GOLDEN_PINAP_BERRY':'Golden Pinap Berry',
        'ITEM_POFFIN':'Poffin','ITEM_GEN5_EVOLUTION_STONE':'Unova Stone',
        'ITEM_GEN4_EVOLUTION_STONE':'Sinnoh Stone',
        'ITEM_TROY_DISK_RAINY':'Rainy Lure','ITEM_TROY_DISK_MAGNETIC':'Magnetic Lure',
        'ITEM_TROY_DISK_GLACIAL':'Glacial Lure','ITEM_TROY_DISK_MOSSY':'Mossy Lure',
        'ITEM_SHADOW_GEM':'Shadow Gem','ITEM_GIOVANNI_MAP':'Shadow Radar',
        'ITEM_LEADER_MAP':'Rocket Radar','ITEM_BEANS':'Beans',
        'ITEM_MOVE_REROLL_ELITE_SPECIAL_ATTACK':'Elite Charged TM',
        'ITEM_MOVE_REROLL_ELITE_FAST_ATTACK':'Elite Fast TM',
        'ITEM_OTHER_EVOLUTION_STONE_A':'Evolution Stone',
        'ITEM_INCUBATOR_SPECIAL':'Special Incubator',
        'FUSION_RESOURCE_DUSKMANE_NECROZMA':'Duskmane Candy',
        'FUSION_RESOURCE_WHITE_KYUREM':'White Kyurem Candy',
        'FUSION_RESOURCE_DAWNWINGS_NECROZMA':'Dawnwings Candy',
        'ITEM_ENHANCED_CURRENCY_HOLDER':'Premium Currency Holder',
        'ITEM_OTHER_EVOLUTION_STONE_MAPLE_A':'Maple Stone A',
        'ITEM_OTHER_EVOLUTION_STONE_MAPLE_C':'Maple Stone C',
    }
    items = {}
    for line in items_raw.group(1).strip().split('\n'):
        parts = line.strip().replace('\t','').rsplit(':',1)
        if len(parts) == 2:
            try: items[parts[0].strip()] = int(parts[1].strip())
            except: pass
    items_df = pd.DataFrame([
        {'item': item_name_map.get(k,k), 'quantity': v}
        for k,v in items.items() if v > 0
    ]).sort_values('quantity', ascending=False)

    # Medals
    medals_raw = re.search(r'You have \d+ medals:\n(.*?)\nVS Seeker', text, re.DOTALL)
    medals = []
    for line in medals_raw.group(1).strip().split('\n'):
        parts = line.strip().replace('\t','').rsplit(':',1)
        if len(parts) == 2:
            medals.append({'medal':parts[0].strip(),'level':parts[1].strip()})
    medals_df = pd.DataFrame(medals)
    medals_df['level'] = pd.to_numeric(medals_df['level'], errors='coerce')
    medals_df = medals_df.dropna(subset=['level'])

    # Recent catches
    log_raw = re.search(r'VS Seeker Status: ACTIVATED\nDate.*?\n(.*?)\nReferral info', text, re.DOTALL)
    catches = []
    for line in log_raw.group(1).strip().split('\n'):
        parts = line.strip().split('\t')
        if len(parts) == 2:
            ts, desc = parts
            if 'was caught!' in desc or 'was hatched!' in desc:
                cp   = re.search(r'CP (\d+)', desc)
                name = re.search(r'^(.*?) was (caught|hatched)', desc)
                if name and cp:
                    method = 'Hatched' if 'hatched' in desc else 'Caught'
                    catches.append({
                        'timestamp': pd.to_datetime(ts, format='mixed', utc=True),
                        'name': clean_name(name.group(1)),
                        'cp': int(cp.group(1)),
                        'method': method,
                        'type': POKEMON_TYPES.get(clean_name(name.group(1)), '?')
                    })
    catches_df = pd.DataFrame(catches)

    return stats, collection_df, type_df, items_df, medals_df, catches_df

# ─────────────────────────────────────────────────────────────────────────────
def load_fitness():
    fit = load_tsv('FitnessData.tsv')
    fit['dt']   = pd.to_datetime(fit['Date and time of logging (UTC)'])
    fit['date'] = fit['dt'].dt.date.astype(str)
    daily = fit.groupby('date').agg({
        'Steps walked':'sum','Calories burned':'sum',
        'Distance travelled (meters)':'sum','Exercise duration (minutes)':'sum',
    }).reset_index()
    daily['km'] = (daily['Distance travelled (meters)'] / 1000).round(2)
    return daily

# ─────────────────────────────────────────────────────────────────────────────
def load_purchases():
    iap = load_tsv('InAppPurchases.tsv')
    iap['dt']    = pd.to_datetime(iap['Date and time'], format='%m/%d/%Y %H:%M:%S UTC', errors='coerce')
    iap['year']  = iap['dt'].dt.year
    iap['month'] = iap['dt'].dt.to_period('M').astype(str)
    spent = iap[iap['Change in pokecoins'] < 0].copy()
    spent['coins'] = spent['Change in pokecoins'].abs()
    by_year  = spent.groupby('year')['coins'].sum().reset_index()
    by_month = spent.groupby('month')['coins'].sum().reset_index()
    item_map = {
        'POKECOIN':'PokéCoins','Poke balls':'Poké Balls',
        'LPSKU_BUNDLE.GENERAL1.FREE.':'Free Daily Bundle',
        'Great balls':'Great Balls','Potion':'Potions',
        'Razz berry':'Razz Berries','ITEM_REMOTE_RAID_TICKET':'Remote Raid Pass',
        'Pokemon storage upgrade':'Storage Upgrade','Bag upgrade':'Bag Upgrade',
        'Ultra balls':'Ultra Balls',
    }
    raw = iap[iap['Item purchased'].notna()]['Item purchased'].value_counts().head(10)
    top_items = pd.DataFrame({'raw':raw.index,'count':raw.values})
    top_items['label'] = top_items['raw'].map(item_map).fillna(top_items['raw'])
    return iap, by_year, by_month, top_items

# ─────────────────────────────────────────────────────────────────────────────
def load_friends():
    friends = load_tsv('FriendList.tsv')
    friends['dt']    = pd.to_datetime(friends['Date of friendship start'])
    friends['year']  = friends['dt'].dt.year
    friends['month'] = friends['dt'].dt.to_period('M').astype(str)
    by_year = friends.groupby('year').size().reset_index(name='new_friends')
    by_year['cumulative'] = by_year['new_friends'].cumsum()
    unf = load_tsv('RecentlyUnfriended.tsv')
    unf['dt'] = pd.to_datetime(unf['Date and time'])
    return friends, by_year, unf

# ─────────────────────────────────────────────────────────────────────────────
def load_encounters():
    extract_journey()
    enc_map = pd.concat([
        parse_ts(load_csv('Map_Pokemon_encounter1.csv')),
        parse_ts(load_csv('Map_Pokemon_encounter2.csv')),
    ]); enc_map['source'] = 'Map'

    enc_lure = pd.concat([
        parse_ts(load_csv('Lure_encounter1.csv')),
        parse_ts(load_csv('Lure_encounter2.csv')),
    ]); enc_lure['source'] = 'Lure'

    enc_inc = pd.concat([
        parse_ts(load_csv('Incense_encounter1.csv')),
        parse_ts(load_csv('Incense_encounter2.csv')),
    ]); enc_inc['source'] = 'Incense'
    enc_inc['Player_Latitude']  = None
    enc_inc['Player_Longitude'] = None

    all_enc = pd.concat([
        enc_map[['ts','source','Player_Latitude','Player_Longitude']],
        enc_lure[['ts','source','Player_Latitude','Player_Longitude']],
        enc_inc[['ts','source','Player_Latitude','Player_Longitude']],
    ], ignore_index=True)

    all_enc['date']  = all_enc['ts'].dt.date.astype(str)
    all_enc['hour']  = all_enc['ts'].dt.hour
    all_enc['year']  = all_enc['ts'].dt.year
    all_enc['month'] = all_enc['ts'].dt.to_period('M').astype(str)
    all_enc['city']  = 'Other'
    all_enc.loc[(all_enc['Player_Latitude']>41)&(all_enc['Player_Latitude']<43),'city'] = 'Boston'
    all_enc.loc[(all_enc['Player_Latitude']>18)&(all_enc['Player_Latitude']<20),'city'] = 'Mumbai'
    return all_enc

# ─────────────────────────────────────────────────────────────────────────────
def load_pokestops():
    extract_journey()
    ps = pd.concat([
        parse_ts(load_csv('Pokestop_spin1.csv')),
        parse_ts(load_csv('Pokestop_spin2.csv')),
    ])
    ps['year']  = ps['ts'].dt.year
    ps['month'] = ps['ts'].dt.to_period('M').astype(str)
    ps['hour']  = ps['ts'].dt.hour
    ps['city']  = 'Other'
    ps.loc[(ps['Player_Latitude']>41)&(ps['Player_Latitude']<43),'city'] = 'Boston'
    ps.loc[(ps['Player_Latitude']>18)&(ps['Player_Latitude']<20),'city'] = 'Mumbai'
    return ps

# ─────────────────────────────────────────────────────────────────────────────
def load_raids():
    extract_journey()
    raids = pd.concat([
        parse_ts(load_csv('Join_Raid_lobby1.csv')),
        parse_ts(load_csv('Join_Raid_lobby2.csv')),
    ])
    raids['year']  = raids['ts'].dt.year
    raids['month'] = raids['ts'].dt.to_period('M').astype(str)
    raids['hour']  = raids['ts'].dt.hour
    return raids

# ─────────────────────────────────────────────────────────────────────────────
def load_gyms():
    extract_journey()
    battles = pd.concat([
        parse_ts(load_csv('Gym_battle1.csv')),
        parse_ts(load_csv('Gym_battle2.csv')),
    ]); battles['type'] = 'Battle'
    deploys = pd.concat([
        parse_ts(load_csv('Deploy_Pokemon1.csv')),
        parse_ts(load_csv('Deploy_Pokemon2.csv')),
    ]); deploys['type'] = 'Deploy'
    feed = pd.concat([
        parse_ts(load_csv('Feed_Pokemon1.csv')),
        parse_ts(load_csv('Feed_Pokemon2.csv')),
    ]); feed['type'] = 'Feed'
    for df in [battles, deploys, feed]:
        df['year']  = df['ts'].dt.year
        df['month'] = df['ts'].dt.to_period('M').astype(str)
    return battles, deploys, feed

# ─────────────────────────────────────────────────────────────────────────────
def load_sessions():
    extract_journey()
    s = parse_ts(pd.read_csv(os.path.join(JOURNEY_DIR,'App_Sessions.csv')), col='Event_time')
    s['year']  = s['ts'].dt.year
    s['month'] = s['ts'].dt.to_period('M').astype(str)
    s['hour']  = s['ts'].dt.hour
    return s

# ─────────────────────────────────────────────────────────────────────────────
def load_map_data():
    """Boston-only GPS points for the live map tab."""
    extract_journey()

    def bos(df, label):
        df = df.copy()
        df['type'] = label
        return boston_filter(df)[['Player_Latitude','Player_Longitude','ts','type']]

    enc_map = pd.concat([
        parse_ts(load_csv('Map_Pokemon_encounter1.csv')),
        parse_ts(load_csv('Map_Pokemon_encounter2.csv')),
    ])
    enc_lure = pd.concat([
        parse_ts(load_csv('Lure_encounter1.csv')),
        parse_ts(load_csv('Lure_encounter2.csv')),
    ])
    pokestops = pd.concat([
        parse_ts(load_csv('Pokestop_spin1.csv')),
        parse_ts(load_csv('Pokestop_spin2.csv')),
    ])
    raids = pd.concat([
        parse_ts(load_csv('Join_Raid_lobby1.csv')),
        parse_ts(load_csv('Join_Raid_lobby2.csv')),
    ])
    deploys = pd.concat([
        parse_ts(load_csv('Deploy_Pokemon1.csv')),
        parse_ts(load_csv('Deploy_Pokemon2.csv')),
    ])

    combined = pd.concat([
        bos(enc_map,   'Catch'),
        bos(enc_lure,  'Lure'),
        bos(pokestops, 'PokeStop'),
        bos(raids,     'Raid'),
        bos(deploys,   'Gym Deploy'),
    ], ignore_index=True)
    combined.columns = ['lat','lon','ts','type']
    return combined

# ─────────────────────────────────────────────────────────────────────────────
def load_all():
    print("Loading all data...")
    extract_journey()
    stats, collection_df, type_df, items_df, medals_df, catches_df = load_gameplay()
    fitness          = load_fitness()
    iap, coins_yr, coins_mo, top_items = load_purchases()
    friends, friends_yr, unf           = load_friends()
    encounters       = load_encounters()
    pokestops        = load_pokestops()
    raids            = load_raids()
    battles, deploys, feed = load_gyms()
    sessions         = load_sessions()
    map_data         = load_map_data()
    print("✅ All data loaded")
    return {
        'stats': stats, 'collection': collection_df, 'types': type_df,
        'items': items_df, 'medals': medals_df, 'catches': catches_df,
        'fitness': fitness, 'iap': iap, 'coins_by_year': coins_yr,
        'coins_by_month': coins_mo, 'top_items': top_items,
        'friends': friends, 'friends_by_year': friends_yr, 'unfriended': unf,
        'encounters': encounters, 'pokestops': pokestops, 'raids': raids,
        'battles': battles, 'deploys': deploys, 'feed': feed,
        'sessions': sessions, 'map_data': map_data,
    }