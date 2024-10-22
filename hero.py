class Hero:
    def __init__(self, info):
        self.stats = info['stats']
        self.weapon = info['weapon']
        self.vitality = info['vitality']
        self.level_up_stats = info['level up']
        self.advanced = info['advanced']

        self.level = 1

    def get_dps(self):
        w_dps = ((float(self.weapon['Bullet Damage']) + \
                  (self.level * float(self.level_up_stats['bullet damage'][1:]))) * \
                  float(self.advanced['Bullets per shot'])) * float(self.weapon['Bullets per sec'])
        return w_dps
    
    # def get_melee_damage(self):
    #     m_dmg = float(self.weapon['Light Melee']) +
    
    def level_up(self):
        self.level += 1