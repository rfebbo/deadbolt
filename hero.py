class Hero:
    def __init__(self, h_info, l_info):
        self.info = h_info
        self.level_info = l_info

        self.items = []
        self.souls = 0


        self.boon_levels = []
        for l in self.level_info:
            if 'm_bUseStandardUpgrade' in self.level_info[l]:
                self.boon_levels.append(int(l))

    def get_dps(self):

        dps_per_level = []
        damage_duration = 10_000
        
        level = 1
        n_boons = 0
        boons = []
        for s in range(0, self.souls+1):

            if s == self.level_info[str(level+1)]['m_unRequiredGold']:
                level += 1

            b_damage = self.info['weapon']['Bullet Damage']
            if level in self.boon_levels and level not in boons:
                boons.append(level)
                n_boons += 1

            b_damage += n_boons * self.info['level_up_upgrades']['MODIFIER_VALUE_BASE_BULLET_DAMAGE_FROM_LEVEL']
            shot_damage = b_damage * self.info['weapon']['Bullets']
            dpm = shot_damage * self.info['weapon']['ClipSize']
            time_to_reloaded_clip = self.info['weapon']['CycleTime'] * self.info['weapon']['ClipSize'] + self.info['weapon']['ReloadDuration']
            mags_to_fire = int(damage_duration / time_to_reloaded_clip)
            damage = mags_to_fire * dpm
            dps = damage / damage_duration
            dps_per_level.append(dps)

        return dps_per_level

    def add_souls(self, souls):
        self.souls += souls

    def add_item(self, item):
        self.items.append(item)
    
    def apply_items(self):
        for i in self.items:
            i.apply(self)