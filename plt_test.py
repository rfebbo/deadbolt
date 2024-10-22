import matplotlib.pyplot as plt
import numpy as np; np.random.seed(1)

x = np.sort(np.random.rand(15))
x2 = np.sort(np.random.rand(15))
y = np.sort(np.random.rand(15))
names = np.array(list("ABCDEFGHIJKLMNO"))

norm = plt.Normalize(1,4)
cmap = plt.cm.RdYlGn

fig,ax = plt.subplots()

lines = []
line, = plt.plot(x,y, marker="o")
lines.append(line)
line, = plt.plot(x2,y, marker="o")
lines.append(line)

annot = ax.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind, l):
    x,y = l.get_data()
    annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
    text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
                           " ".join([names[n] for n in ind["ind"]]))
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)

(last_l, last_ind) = (None, None)

def hover(event):
    global last_l, last_ind
    vis = annot.get_visible()
    if event.inaxes == ax:
        for l in lines:
            cont, ind = l.contains(event)
            if cont:
                if last_l != l or last_ind != ind:
                    last_l = l
                    last_ind = ind
                    update_annot(ind, l)
                    fig.canvas.draw_idle()
                annot.set_visible(True)
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

plt.show()