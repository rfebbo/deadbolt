from slpp import slpp as lua
import json

heroes_to_ignore = ['kali', 'gunslinger', 'yakuza', 'genericperson',\
                    'tokamak', 'rutger', 'thumper', 'cadence', 'targetdummy',\
                    'bomber', 'shieldguy', 'vandal', 'operative']

heroes_lua = {}
items_lua = {}
abilities_lua = {}

with open('./assets/data/raw/heroes.lua', 'r') as f:

    heroes_file = lua.decode(f.read())

    for h in heroes_file:
        if isinstance(heroes_file[h], dict):
            skip = False
            for i in heroes_to_ignore:
                if i in h:
                    skip = True
            if skip:
                continue
            heroes_lua[h] = heroes_file[h]


with open('./assets/data/raw/abilities.lua', 'r') as f:

    abilities_file = lua.decode(f.read())

    for a in abilities_file:
        if isinstance(abilities_file[a], dict):
            if 'upgrade' in a:
                items_lua[a] = abilities_file[a]
            else:
                abilities_lua[a] = abilities_file[a]





name_mappings = {} 
with open('./assets/data/raw/citadel_gc_english.txt', 'r') as f:
    for line in f:
        if '//' in line:
            continue
        line = line.split('"')
        if len(line) != 5:
            continue
        name_mappings[line[1]] = line[-2].strip()

items = {}

tiers = ['Tier_1', 'Tier_2', 'Tier_3', 'Tier_4']
types = ['Weapon', 'Armor', 'Tech']

for type in types:
    items[type] = {}
    for tier in tiers:
        items[type][tier] = []


n_items = 0
for i in items_lua:
    if i not in name_mappings:
        continue
    n_items += 1
    i_dict = {}

    i_dict['name'] = name_mappings[i]


    if 'm_mapAbilityProperties' in items_lua[i]:
        i_dict['Properties'] = []
        for p in items_lua[i]['m_mapAbilityProperties']:
            if items_lua[i]['m_mapAbilityProperties'][p]['m_strValue'] != '0':
                if p == 'AbilityUnitTargetLimit':
                    continue
                if p == 'ChannelMoveSpeed' and items_lua[i]['m_mapAbilityProperties'][p]['m_strValue'] == '50':
                    continue
                prop = {}
                prop['name'] = p
                prop['value'] = items_lua[i]['m_mapAbilityProperties'][p]['m_strValue']
                i_dict['Properties'].append(prop)



    if "m_iItemTier" in items_lua[i]:
        for tier in tiers:
            if  tier in items_lua[i]['m_iItemTier']:
                if items_lua[i]['_editor']['folder_name'] in items:
                    items[items_lua[i]['_editor']['folder_name']][tier].append(i_dict)

print(n_items)
json.dump(items, open('./assets/data/processed/items.json', 'w'), indent=4)

ability_mappings = {}
with open('./assets/data/raw/citadel_heroes_english.txt', 'r') as f:
    for line in f:
        if '//' in line:
            continue
        line = line.replace('citadel_weapon_hero', 'citadel_weapon')
        line = line.replace('atlas', 'bull')
        line = line.replace('forge', 'engineer')
        # dynamo, sumo
        line = line.replace('dynamo','sumo')
        # orion, archer
        line = line.replace('orion', 'archer')
        # kill, digger
        line = line.replace('krill', 'digger')
        line = line.split('"')
        if len(line) != 5:
            continue
        ability_mappings[line[1]] = line[-2].strip()

heroes = {}

heroes['heroes'] = []

for h in heroes_lua:
    if h not in name_mappings:
        continue
    h_dict = {}
    h_dict['abilities'] = {}
    h_dict['iname'] = h
    h_dict['name'] = name_mappings[h]

    # m_mapPurchaseBonuses

    # m_mapStandardLevelUpUpgrades
    h_dict['level_up_upgrades'] = heroes_lua[h]['m_mapStandardLevelUpUpgrades']
    # m_mapStartingStats
    h_dict['starting_stats'] = heroes_lua[h]['m_mapStartingStats']
    ss_to_remove = ['EWeaponPower', 'ECrouchSpeed', 'EMoveAcceleration',\
                    'EReloadSpeed', 'EWeaponPowerScale', 'EProcBuildUpRateScale', 'EStaminaRegenPerSecond'\
                    'EAbilityResourceMax', 'EAbilityResourceRegenPerSecond', 'ETechDuration', 'ETechRange']
    for ss in ss_to_remove:
        if ss in h_dict['starting_stats']:
            h_dict['starting_stats'].pop(ss)

    # m_mapBoundAbilities
    h_dict['abilities'] = []
    for i in range(4):
        int_ability_name = heroes_lua[h]['m_mapBoundAbilities'][f'ESlot_Signature_{i+1}']
        if int_ability_name not in ability_mappings:
            continue
        h_dict['abilities'].append(ability_mappings[int_ability_name])


    int_weapon_name = heroes_lua[h]['m_mapBoundAbilities']['ESlot_Weapon_Primary']
    if int_weapon_name not in abilities_lua:
        continue
    weapon = {}
    # m_Spread
    weapon['Spread'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_Spread']
    # m_StandingSpread
    weapon['StandingSpread'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_StandingSpread']
    # m_flScatterYawScale
    weapon['ScatterYawScale'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flScatterYawScale']
    # m_flVerticalPunch
    weapon['VerticalPunch'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flVerticalPunch']
    # m_flRecoilRecoverySpeed
    weapon['RecoilRecoverySpeed'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flRecoilRecoverySpeed']
    # m_iBullets
    weapon['Bullets'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_iBullets']
    # m_flCycleTime
    weapon['CycleTime'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flCycleTime']
    # m_reloadDuration
    weapon['ReloadDuration'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_reloadDuration']
    # m_iClipSize
    weapon['ClipSize'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_iClipSize']
    # m_flBulletRadius
    weapon['Bullet Radius'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flBulletRadius']
    # m_bSpinsUp
    if 'm_bSpinsUp' in abilities_lua[int_weapon_name]['m_WeaponInfo']:
        weapon['SpinsUp'] = int(abilities_lua[int_weapon_name]['m_WeaponInfo']['m_bSpinsUp'])
    # m_flMaxSpinCycleTime
    if 'm_flMaxSpinCycleTime' in abilities_lua[int_weapon_name]['m_WeaponInfo']:
        weapon['MaxSpinCycleTime'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flMaxSpinCycleTime']
    # m_flSpinIncreaseRate
    if 'm_flSpinIncreaseRate' in abilities_lua[int_weapon_name]['m_WeaponInfo']:
        weapon['SpinIncreaseRate'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flSpinIncreaseRate']
    # m_flSpinDecayRate
    if 'm_flSpinDecayRate' in abilities_lua[int_weapon_name]['m_WeaponInfo']:
        weapon['SpinDecayRate'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flSpinDecayRate']
    # m_flSpreadPerShot
    if 'm_flSpreadPerShot' in abilities_lua[int_weapon_name]['m_WeaponInfo']:
        weapon['SpreadPerShot'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flSpreadPerShot']
    # m_flBulletDamage
    weapon['Bullet Damage'] = abilities_lua[int_weapon_name]['m_WeaponInfo']['m_flBulletDamage']
    h_dict['weapon'] = weapon
    h_dict['weapon_name'] = ability_mappings[int_weapon_name]

    h_dict['image_location'] = f'mm_images/{h[5:]}_mm_psd.png'
    heroes['heroes'].append(h_dict)
    
print(len(heroes))
json.dump(heroes, open('./assets/data/processed/heroes.json', 'w'), indent=4)

level_bonuses = heroes_lua[h]['m_mapLevelInfo']


lb = {'levels': level_bonuses}

json.dump(lb, open('./assets/data/processed/level_bonuses.json', 'w'), indent=4)

item_bonuses = heroes_lua[h]['m_mapPurchaseBonuses']
json.dump(item_bonuses, open('./assets/data/processed/item_bonuses.json', 'w'), indent=4)
