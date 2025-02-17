class Item:
    def __init__(self, info):
        self.info = info
        self.name = info['m_strCSSClass']
        self.effects = None

    def apply(self, hero):
        pass
        

