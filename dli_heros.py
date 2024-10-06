import json
import regex as re
from bs4 import BeautifulSoup
import requests

heros = {'Abrams' : {}, 'Bebop' : {}, 'Dynamo' : {}, 'Grey_Talon' : {}, 'Haze' : {}, \
         'Infernus' : {}, 'Ivy': {}, 'Kelvin' : {}, 'Lady_Geist' : {}, 'Lash' : {}, \
         'McGinnis' : {}, 'Mo_and_Krill' : {}, 'Paradox' : {}, 'Pocket' : {}, \
         'Seven' : {}, 'Shiv' : {}, 'Vindicta' : {}, 'Viscous' : {}, 'Warden' : {}, 'Wraith' : {}, 'Yamato' : {}}

# heros = {'Abrams' :  {}}
# heros = {'Yamato' :  {}}
# heros = {'McGinnis' :  {}}

def pp(j):
    print(json.dumps(j, indent=4))

def scrape_li(soup):
    grab_next = False
    scrape = []

    for l in soup.split('\n'):
        if grab_next:
            scrape.append(l.strip())
            grab_next = False
        elif '<li>' in l:
            grab_next = True
    
    return scrape

def get_base_stats(hero):
    page = requests.get(f'https://deadlockwiki.org/w/{hero}')
    
    soup = BeautifulSoup(page.content, 'html.parser').prettify()

    idx1 = soup.find('hero-infobox-table')
    idx2 = soup.find('citizen-section-heading')


    soup = soup[idx1:idx2]
    soup = soup.replace('\n','').replace(' ', '').replace('\t', '').strip()
    # print(soup)


    stats = {'DPS' : 0, 'Health' : 0, 'Speed' : 0, 'Stamina' : 0}



    for s in stats:
        res = re.findall(f'<b>{s}</b></td><tdclass="hero-infobox-right">(\d+|\d+\.?\d?m/s)(<spantitle="Spiritscaling"|</td></tr><tr><tdclass="hero-infobox-left")', soup)
        for r in res:
            if s == 'Speed':
                stats[s] = r[0][:-3]
            else:
                stats[s] = r[0]
    return stats

def get_weapon_stats(hero):
    page = requests.get(f'https://deadlockwiki.org/w/{hero}')
    
    soup = BeautifulSoup(page.content, 'html.parser').prettify()
    
    idx1 = soup.find('Weapon:')
    idx2 = soup.find('Vitality:')
    soup = soup[idx1:idx2]
    # print(soup)
    n_attr = 0
    grab_next = False
    scrape = []

    for l in soup.split('\n'):
        if grab_next:
            scrape.append(l.strip())
            grab_next = False
        elif '<li>' in l:
            n_attr += 1
            grab_next = True

    soup = soup.replace('\n','').replace(' ', '').replace('\t', '').strip()
    
    weapon = {}
    infos = ['name', 'DPS', 'Bullet Damage', 'Ammo', 'Ammo scaling',\
              'Bullets per sec', 'Bullet per sec scaling','Light Melee', 'Heavy Melee']
    
    

    for i in range(len(infos)):
        idx1 = soup.find('<li>')
        idx2 = soup.find('</li>')
        soup_info = soup[idx1+4:idx2].lower()
        # print(f'selecting {i} {soup_info}')
        for inf in infos:
            i_actual = inf.lower().replace(' ', '')
            # print(f'\tsearching {i_actual}')
            if inf == 'name' and i == 0: 
                weapon['name'] = soup[idx1+4:idx2]
            elif i_actual in soup_info:
                # print(f'\t\tfound {i_actual}')
                if 'scaling' not in soup_info and 'scaling' not in i_actual:
                    weapon[inf] = soup[idx1+4:idx2-len(i_actual)]
                    # print(f'\t\t\tadding {i_actual}')
                elif 'scaling' in i_actual and 'scaling' in soup_info:
                    if ':' in soup_info:
                        # print(f'\t\t\tadding {i_actual}')
                        weapon[inf] = soup[idx1+6+len(i_actual):idx2]
                    else:
                        # print(f'\t\t\tadding {i_actual}')
                        weapon[inf] = soup[idx1+5:idx2-len(i_actual)]
                    
        soup = soup[idx2+5:]

    if n_attr > len(weapon.keys()):
        print(f'missed {n_attr-len(weapon.keys())} attributes in weapon for {hero}')
        # print(scrape)
        pp(weapon)

    return weapon

def get_vitality_stats(hero):
    page = requests.get(f'https://deadlockwiki.org/w/{hero}')
    
    soup = BeautifulSoup(page.content, 'html.parser').prettify()
    # print(soup)
    idx1 = soup.find('Vitality:')
    idx2 = soup.find('Level up:')
    soup = soup[idx1:idx2]
    # print(soup)
    n_attr = 0
    for l in soup.split('\n'):
        if '<li>' in l:
            n_attr += 1

    soup = soup.replace('\n','').replace(' ', '').replace('\t', '').strip()

    vitality = {}
    infos = ['Max Health', 'Health Regen', '%Bullet Resist', '%Spirit Resist',\
             'm/smove Speed','move Speed scaling', 'm/sSprint Speed','sprint Speed scaling', 'Stamina', 'Headshot']
    
    for i in range(len(infos)):
        idx1 = soup.find('<li>')
        idx2 = soup.find('</li>')
        for inf in infos:
            i_actual = inf.lower().replace(' ', '')
            if i_actual in soup[idx1+4:idx2].lower():
                if 'scaling' in inf:
                    vitality[inf] = soup[idx1+5:idx2-len(i_actual)]
                else:
                    vitality[inf.replace('m/s', '').replace('%','')] = soup[idx1+4:idx2-len(i_actual)]
        soup = soup[idx2+5:]

    if n_attr > len(vitality.keys()):
        print(f'missed {n_attr-len(vitality.keys())} attributes in vitality for {hero}')
        pp(vitality)

    return vitality

def get_levelup_stats(hero):
    page = requests.get(f'https://deadlockwiki.org/w/{hero}')
    
    soup = BeautifulSoup(page.content, 'html.parser').prettify()
    # print(soup)
    idx1 = soup.find('Level up:')
    idx2 = soup.find('Advanced:')
    soup = soup[idx1:idx2]
    
    n_attr = 0
    for l in soup.split('\n'):
        if '<li>' in l:
            n_attr += 1

    soup = soup.replace('\n','').replace(' ', '').replace('\t', '').strip()

    levelup = {}
    infos = ['bullet damage', 'base melee damage', 'base health', 'bullet resist', 'weapon range']
    
    for i in range(len(infos)):
        idx1 = soup.find('<li>')
        idx2 = soup.find('</li>')
        for inf in infos:
            i_actual = inf.lower().replace(' ', '')
            if i_actual in soup[idx1+4:idx2].lower():
                if 'scaling' in inf:
                    levelup[inf] = soup[idx1+5:idx2-len(i_actual)]
                else:
                    levelup[inf] = soup[idx1+4:idx2-len(i_actual)]
        soup = soup[idx2+5:]


    if n_attr > len(levelup.keys()):
        print(f'missed {n_attr-len(levelup.keys())} attributes in levelup for {hero}')
        pp(levelup)
        
    # print(soup[idx1:idx2])

    return levelup

def get_advanced_stats(hero):
    page = requests.get(f'https://deadlockwiki.org/w/{hero}')
    
    soup = BeautifulSoup(page.content, 'html.parser').prettify()
    # print(soup)
    idx1 = soup.find('Advanced:')
    idx2 = soup[idx1:].find('citizen-section-heading') + idx1
    soup = soup[idx1:idx2]
    # print(soup)
    
    attributes = scrape_li(soup)
    n_attr = len(attributes)
    # print(attributes)

    soup = soup.replace('\n','').replace(' ', '').replace('\t', '').strip()

    advanced = {}
    infos = [
    'Time per bullet',
    'Bullets per second',
    'Bullet radius',
    'Bullet spread increase per bullet',
    'Bullet spread',
    'Bullets per shot',
    'Bullet speed',
    'Reload time',
    'Magazine size',
    'Magazine size scaling',
    'Pellet spread',
    'Reload type',
    'Bullet lifetime',
    'Bullet gravity scale',
    'Bullet range',
    'Falloff Range',
    'Burst amount',
    'Burst cycletime',
    'Recoil punch',
    'Weapon windup speed',
    'Weapon windup decay',
    'Has recoil']
    
    for i in range(len(attributes)):
        idx1 = soup.find('<li>')
        idx2 = soup.find('</li>')
        for inf in infos:
            i_actual = inf.lower().replace(' ', '')
            l_label = inf

            if l_label in advanced:
                l_label += " secondary"

            if i_actual in soup[idx1+4:idx2].lower():
                
                if 'scaling' in inf:
                    advanced[l_label] = soup[idx1+6+len(i_actual):idx2]
                else:
                    advanced[l_label] = soup[idx1+5+len(i_actual):idx2]
        soup = soup[idx2+5:]


    if n_attr > len(advanced.keys()):
        print(f'missed {n_attr-len(advanced.keys())} attributes in advanced for {hero}')
        pp(advanced)
        
    # print(soup[idx1:idx2])

    return advanced

def get_abilities(hero):
    page = requests.get(f'https://deadlockwiki.org/w/{hero}')
    
    soup = BeautifulSoup(page.content, 'html.parser').prettify()
    # print(soup)
    idx1 = soup.find('Abilities')
    soup = soup[idx1:]
    print(soup)
    idx2 = soup.find('Default build')
    soup = soup[0:idx2]
    print(soup)
    
    attributes = scrape_li(soup)
    n_attr = len(attributes)
    print(attributes)

    soup = soup.replace('\n','').replace(' ', '').replace('\t', '').strip()

    advanced = {}
    infos = [
    'Time per bullet',
    'Bullets per second',
    'Bullet radius',
    'Bullet spread increase per bullet',
    'Bullet spread',
    'Bullets per shot',
    'Bullet speed',
    'Reload time',
    'Magazine size',
    'Magazine size scaling',
    'Pellet spread',
    'Reload type',
    'Bullet lifetime',
    'Bullet gravity scale',
    'Bullet range',
    'Burst amount',
    'Burst cycletime',
    'Recoil punch',
    'Weapon windup speed',
    'Weapon windup decay',
    'Has recoil']
    
    for i in range(len(attributes)):
        idx1 = soup.find('<li>')
        idx2 = soup.find('</li>')
        for inf in infos:
            i_actual = inf.lower().replace(' ', '')
            l_label = inf

            if l_label in advanced:
                l_label += " secondary"

            if i_actual in soup[idx1+4:idx2].lower():
                
                if 'scaling' in inf:
                    advanced[l_label] = soup[idx1+6+len(i_actual):idx2]
                else:
                    advanced[l_label] = soup[idx1+5+len(i_actual):idx2]
        soup = soup[idx2+5:]


    if n_attr > len(advanced.keys()):
        print(f'missed {n_attr-len(advanced.keys())} attributes in advanced for {hero}')
        pp(advanced)
        
    # print(soup[idx1:idx2])

    return advanced

def download_hero_info():
    for h in heros:
        heros[h]['stats'] = get_base_stats(h)
        heros[h]['weapon'] = get_weapon_stats(h)
        heros[h]['vitality'] = get_vitality_stats(h)
        heros[h]['level up'] = get_levelup_stats(h)
        heros[h]['advanced'] = get_advanced_stats(h)
        # heros[h]['abilities'] = get_abilities(h)
        

    with open('./info/heros/deadlock_hero_info.json', 'w') as f:
        f.write(json.dumps(heros, indent=4))

def load_local_heros():
    deadlock_hero_info = {}
    with open('./info/heros/deadlock_hero_info.json', 'r') as f:
        deadlock_hero_info = json.loads(f.read())

    return deadlock_hero_info