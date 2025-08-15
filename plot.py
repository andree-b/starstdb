import tkinter

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt
from mplcursors import cursor
from starstdb import starstdb

import numpy as np


def plot(gfilter):
    db = starstdb()
    #data = db.get_days()
    data = db.get_tournaments()
    print(len(data))

    root = tkinter.Tk()
    root.wm_title("Embedding in Tk")

    fig = Figure(figsize=(5, 5), dpi=100)

    #print(data)
    #data=sorted(data, key=0)
    data = sorted(data, key=lambda cols: cols[9], reverse = False)
    x  = [row[9][0:10] for row in data]
    y1 = np.cumsum([row[7] for row in data])
    y2 = np.cumsum([row[3] for row in data])
    y3 = y1-y2
    #print(x)
    #rint(y1)
    p = fig.add_subplot(111)

    p.set(xlabel='# of tournaments', ylabel='Amount in $',
           title='starstdb')
    p.plot(y1, "-", label="cashes", drawstyle='steps-mid')
    p.plot(y2, "--", label="buyins", drawstyle='steps-mid')
    p.plot(y3, ":", label="result", drawstyle='steps-mid')
    p.legend(loc='upper left')

    p.grid(axis = 'y')
    locs = p.get_xticks()[1:]
    #print(locs)
    nlabs = []
    for x1 in locs:
        #x2 = int(round(x1*len(x)))
        x2=int(x1)
        if x2>=0 and x2<len(x):
            nlabs.append("%d - %s" % (x2,x[x2]))
        else:
            nlabs.append("")
    #print(nlabs)
    p.set_xticks(locs, nlabs, rotation='vertical')

    def show_annotation(sel):
        xi, yi = sel.target
        xi = int(round(xi))
        sel.annotation.set_text(f'{x[xi]}\nvalue:{yi:.3f}')

    c = cursor(p.get_lines(), hover=True)
    c.connect('add', show_annotation)
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()


    #def on_key_press(event):
    #    print("you pressed {}".format(event.key))
    #    key_press_handler(event, canvas, toolbar)


    #canvas.mpl_connect("key_press_event", on_key_press)

    button = tkinter.Button(master=root, text="Close", command=root.destroy)

    # Packing order is important. Widgets are processed sequentially and if there
    # is no space left, because the window is too small, they are not displayed.
    # The canvas is rather flexible in its size, so we pack it last which makes
    # sure the UI controls are displayed as long as possible.
    button.pack(side=tkinter.BOTTOM)
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

if __name__ == "__main__":
    plot()
    tkinter.mainloop()
