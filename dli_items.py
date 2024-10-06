import json
import regex as re
from bs4 import BeautifulSoup
import requests
import os

from dli_heros import pp


items = {}

items['Weapons'] = {}
items['Weapons']['T1'] = {
    'Basic Magazine' : {},
    'Close Quarters' : {},
    'Headshot Booster' : {},
    'High-Velocity Mag' : {},
    'Hollow Point Ward' : {},
    'Monster Rounds' : {},
    'Rapid Rounds' : {},
    'Restorative Shot' : {}
}
items['Weapons']['T2'] = {
    'Active Reload' : {},
    'Berserker' : {},
    'Kinetic Dash' : {},
    'Long Range' : {},
    'Melee Charge' : {},
    'Mystic Shot' : {},
    'Slowing Bullets' : {},
    'Soul Shredder Bullets' : {},
    'Swift Striker' : {},
    'Fleetfoot' : {}
}
items['Weapons']['T3'] = {
    'Burst Fire' : {},
    'Escalating Resilience' : {},
    'Headhunter' : {},
    'Hunters Aura' : {},
    'Intensifying Magazine' : {},
    'Point Blank' : {},
    'Pristine Emblem' : {},
    'Sharpshooter' : {},
    'Tesla Bullets' : {},
    'Titanic Magazine' : {},
    'Toxic Bullets' : {},
    'Alchemical Fire' : {},
    'Heroic Aura' : {},
    'Warp Stone' : {}
}

items['Weapons']['T4'] = {
    'Crippling Headshot' : {},
    'Frenzy' : {},
    'Glass Cannon' : {},
    'Lucky Shot' : {},
    'Ricochet' : {},
    'Siphon Bullets' : {},
    'Spiritual Overflow' : {},
    'Silencer' : {},
    'Vampiric Burst' : {}
}

items['Vitality'] = {}

items['Vitality']['T1'] = {
    'Enduring Spirit' : {},
    'Extra Health' : {},
    'Extra Regen' : {},
    'Extra Stamina' : {},
    'Melee Lifesteal' : {},
    'Sprint Boots' : {},
    'Healing Rite' : {}
}

items['Vitality']['T2'] = {
    'Bullet Armor' : {},
    'Bullet Lifesteal' : {},
    'Combat Barrier' : {},
    'Debuff Reducer' : {},
    'Enchanters Barrier' : {},
    'Enduring Speed' : {},
    'Healbane' : {},
    'Healing Booster' : {},
    'Reactive Barrier' : {},
    'Spirit Armor' : {},
    'Spirit Lifesteal' : {},
    'Divine Barrier' : {},
    'Health Nova' : {},
    'Restorative Locket' : {},
    'Return Fire' : {}
}

items['Vitality']['T3'] = {
    'Fortitude' : {},
    'Improved Bullet Armor' : {},
    'Improved Spirit Armor' : {},
    'Lifestrike' : {},
    'Superior Stamina' : {},
    'Veil Walker' : {},
    'Debuff Remover' : {},
    'Majestic Leap' : {},
    'Metal Skin' : {},
    'Rescue Beam' : {}
}

items['Vitality']['T4'] = {
    'Inhibitor' : {},
    'Leech' : {},
    'Soul Rebirth' : {},
    'Colossus' : {},
    'Phantom Strike' : {},
    'Shadow Weave' : {},
    'Unstoppable' : {}
}


items['Spirit'] = {}

items['Spirit']['T1'] = {
    'Ammo Scavenger' : {},
    'Extra Charge' : {},
    'Extra Spirit' : {},
    'Mystic Burst' : {},
    'Mystic Reach' : {},
    'Spirit Strike' : {},
    'Infuser' : {}
}

items['Spirit']['T2'] = {
    'Bullet Resist Shredder' : {},
    'Duration Extender' : {},
    'Improved Cooldown' : {},
    'Mystic Vulnerability' : {},
    'Quicksilver Reload' : {},
    'Suppressor' : {},
    'Cold Front' : {},
    'Decay' : {},
    'Slowing Hex' : {},
    'Withering Whip' : {}
}

items['Spirit']['T3'] = {
    'Improved Burst' : {},
    'Improved Reach' : {},
    'Improved Spirit' : {},
    'Mystic Slow' : {},
    'Rapid Recharge' : {},
    'Superior Cooldown' : {},
    'Superior Duration' : {},
    'Surge of Power' : {},
    'Torment Pulse' : {},
    'Ethereal Shift' : {},
    'Knockdown' : {},
    'Silence Glyph' : {}
}

items['Spirit']['T4'] = {
    'Boundless Spirit' : {},
    'Diviners Kevlar' : {},
    'Escalating Exposure' : {},
    'Mystic Reverb' : {},
    'Curse' : {},
    'Echo Shard' : {},
    'Magic Carpet' : {},
    'Refresher' : {}
}

def scrape_li_items(soup):
    grab_next = False
    scrape = []

    for l in soup.split('\n'):
        if '<li>' in l:
            scrape.append([])
            grab_next = True
        elif '</li>' in l:
            grab_next = False
        elif grab_next:
            scrape[-1].append(l.strip())

    return scrape

def get_percent(string):
    idx1 = string.find('%')
    # print(string[0:idx1])
    return string[0:idx1]

def get_item_attributes(item):
    url_name = item.replace(' ', '_')

    
    soup = ''
    with open(f'./info/items/item_pages/{url_name}.txt', 'r') as f:
        soup = f.read()
    # print(soup)
    idx1 = soup.find('Attributes')
    soup = soup[idx1:]
    # print(soup)
    # idx2 = soup.find('Effects')
    idx2 = soup.find('</ul>')
    soup = soup[0:idx2]
    # print(soup)
    att = scrape_li_items(soup)
    # print(att)

    attributes = {}
    a_types = ['Tier', 'Cost', 'Bonus Health', 'Bullet Resist', 'Ammo',\
                'Weapon Damage', 'component of', 'Bullet Shield Health', 'Weapon Damage', 'Fire Rate', 'Bullet Shield Health', 'Head Shot Bonus Damage']
    for a in att:
        for at in a_types:
            if at in a[0]:
                if 'Cost' in at:
                    attributes[at] = a[-1]
                elif 'component' in at:
                    attributes[at] = a[2]
                elif 'Tier' in at:
                    attributes[at] = a[0][len(at)+2:]
                elif '%' in a[0]:
                    attributes[at] = get_percent(a[0])
                else:
                    attributes[at] = a[0]
    # print(attributes)
    rv = 0
    n_missing_attributes = len(att) - len(attributes.items())
    if n_missing_attributes > 0:

        print(f'missing {n_missing_attributes} attributes from {item}')
        pp(attributes)
        # print(att)
        rv = 1

    return attributes, rv

def get_item_effects(item):
    url_name = item.replace(' ', '_')

    soup = ''
    with open(f'./info/items/item_pages/{url_name}.txt', 'r') as f:
        soup = f.read()
    # print(soup)
    idx1 = soup.find('Effects')
    soup = soup[idx1:]
    # print(soup)
    idx2 = soup.find('</ul>')
    soup = soup[0:idx2]
    # print(soup)
    att = scrape_li_items(soup)
    # print(att)

    effects = {}
    a_types = ['Bonus Health', 'Bullet Resist', 'Duration', 'Passive', 'Weapon Damage within']
    for a in att:
        for at in a_types:
            if at in a[0]:
                if 'Duration' in at:
                    effects[at] = a[0:-len(at)-2]
                elif 'Cost'  in at:
                    effects[at] = a[6:-6]
                elif '%' in a:
                    effects[at] = get_percent(a)
                else:
                    effects[at] = a
                
    # print(effects)
    rv = 0
    n_missing_effects = len(att) - len(effects.items())
    if n_missing_effects > 0:

        print(f'missing {n_missing_effects} effects from {item}')
        
        pp(effects)
        print(att)
        rv = 1

    return effects, rv

def download_item_page(item):
    url_name = item.replace(' ', '_')

    page = requests.get(f'https://deadlockwiki.org/w/{url_name}')
    
    soup = BeautifulSoup(page.content, 'html.parser').prettify()
    with open(f'./info/items/item_pages/{url_name}.txt', 'w', encoding='utf-8') as f:
        for l in soup.split('\n'):
            f.write(str(l.encode('utf8'))[2:] + '\n')

def download_item_info():
    local_items = os.listdir('./info/items/item_pages/')
    
    for type in items:
        for tier in items[type]:
            for name in items[type][tier]:
                if name.replace(' ', '_') + '.txt' not in local_items:
                    download_item_page(name)
                    
                items[type][tier][name]['attributes'], rv1 = get_item_attributes(name)
                items[type][tier][name]['effects'], rv2 = get_item_effects(name)
                
                # if rv1 != 0 or rv2 != 0:
                # pp(items[type][tier][name])
                # return
                    


        

        with open(f'./info/items/{type}_item_info.json', 'w') as f:
            f.write(json.dumps(items[type], indent=4))


