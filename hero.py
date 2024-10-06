class hero:
    def __init__(self, info):
        self.stats = info['stats']
        self.weapon = info['weapon']
        self.vitality = info['vitality']
        self.level_up = info['level up']
        self.advanced = info['advanced']

    def get_dps(self):
        w_dps = (float(self.weapon['Bullet Damage']) * float(self.advanced['Bullets per shot'])) * float(self.weapon['Bullets per sec'])
        return w_dps