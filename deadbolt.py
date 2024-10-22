import numpy as np
import matplotlib.pyplot as plt

from dli_heros import load_local_heros, download_hero_info
from dli_items import download_item_info
from hero import Hero


download_hero_info()

heros = load_local_heros()
# download_item_info()

names = heros.keys()
fig,ax = plt.subplots()

annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind):
    x,y = line.get_data()
    annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
    text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
                           " ".join([names[n] for n in ind["ind"]]))
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)


def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = line.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

for name in heros:
    dmg = []
    lvl = []
    h = Hero(heros[name])
    print(f'{name} DPS:{h.get_dps()}')

    for i in range(10):
        dmg.append(h.get_dps())
        lvl.append(i)
        h.level_up()

    plt.plot(lvl, dmg, label=name)

plt.legend()
plt.show()
# download_hero_info()
download_item_info()

    



