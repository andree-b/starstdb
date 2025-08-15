from tksheet import (
    Sheet,
    formatter,
    num2alpha,
    float_formatter)
import tkinter as tk
import logging
import os
from ts_parser import TS_parser
from hh_parser import HH_parser
from plot import plot

class gui(tk.Tk):
    def __init__(self, title, db, config):
        tk.Tk.__init__(self)
        self.log = logging.getLogger("starstdb")
                
        self.title(title)
        self.db=db
        self.config=config

        # build the main window
        self.frame = tk.Frame(self)
        self.frame.pack()
        f1=tk.Frame(self.frame)
        f1.pack(fill=tk.X)
        f2=tk.Frame(self.frame)
        f2.pack(fill=tk.X)
        f3=tk.Frame(self.frame)
        f3.pack(fill=tk.X)
        f4=tk.Frame(self.frame)
        f4.pack(fill=tk.X)
        f5=tk.Frame(self.frame)
        f5.pack(fill=tk.X)

        
        button = tk.Button(f1, text='List of Tournaments', width=30, command=self.open_tournaments)
        button.pack(fill=tk.Y, side=tk.LEFT)
        button = tk.Button(f1, text='Reset', width=30, command=self.db_reset)
        button.pack(fill=tk.Y, side=tk.LEFT)
        
        button = tk.Button(f2, text='List of Games', width=30, command=self.open_games)
        button.pack(fill=tk.Y, side=tk.LEFT)
        button = tk.Button(f2, text='Parse Logs', width=30, command=self.parse)
        button.pack(fill=tk.Y, side=tk.LEFT)
        
        button = tk.Button(f3, text='List of Days', width=30, command=self.open_days)
        button.pack(fill=tk.Y, side=tk.LEFT)
        button = tk.Button(f3, text='Parse HH', width=30, command=self.parse_hh)
        button.pack(fill=tk.Y, side=tk.LEFT)

        button = tk.Button(f4, text='Plot', width=30, command=self.open_plot)
        button.pack(fill=tk.Y, side=tk.LEFT)

        # Dropdown options  
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]  

        # Selected option variable  
        opt = tk.StringVar(value="Monday")  

        combo = tk.OptionMenu(f4, opt, *days)
        combo.pack(fill=tk.Y, side=tk.LEFT)
        
        #button = tk.Button(f4, text='Exit', width=30, command=self.destroy)
        #button.pack(fill=tk.Y, side=tk.LEFT)


        button = tk.Button(f5, text='Config', width=30, command=self.edit_config)
        button.pack(fill=tk.Y, side=tk.LEFT)
        button = tk.Button(f5, text='Exit', width=30, command=self.destroy)
        button.pack(fill=tk.Y, side=tk.LEFT)


        

    def db_reset(self):
        self.db.reset_tables()

    def parse(self):
        tdir = r"%s\TournSummary\%s" % (self.config["main"]["dirname"], self.config["main"]["player"])
        p = TS_parser(self.db, self.config).parse_dir(tdir)
                                       

    def parse_hh(self):
        hdir = r"%s\HandHistory\%s" % (self.config["main"]["dirname"], self.config["main"]["player"])
        #p = HH_parser(self.db, self.config).parse_file(r"C:\Users\andre\AppData\Local\PokerStars.DE\HandHistory\andree_b\HH20240602 T3759789633 No Limit 2-7 Single Draw $9.80 + $1.20.txt")
        p = HH_parser(self.db, self.config).parse_dir(hdir)

    def open_tournaments(self):
        self.log.info("gui.open_tournaments");
        t=gui_table("Tournaments", self.db.get_tournaments())
        t.sheet.set_header_data("T#ID", 0)
        t.sheet.set_header_data("Game", 1)
        t.sheet.column_width(1, 200)
        t.sheet.set_header_data("Currency", 2)
        t.sheet.column_width(2, 64)
        t.sheet.set_header_data("Total", 3)
        t.sheet.column_width(3, 80)
        t.sheet.span(num2alpha(3)).format(float_formatter(decimals = 2)) 
        t.sheet.set_header_data("Buyin", 4)
        t.sheet.column_width(4, 80)
        t.sheet.set_header_data("Rake", 5)
        t.sheet.column_width(5, 80)
        t.sheet.set_header_data("Entries", 6)
        t.sheet.column_width(6, 64)
        t.sheet.set_header_data("Cash", 7)
        t.sheet.column_width(7, 80)
        t.sheet.set_header_data("Bounties", 8)
        t.sheet.column_width(8, 80)
        t.sheet.span(num2alpha(8)).format(float_formatter(decimals = 2))
        t.sheet.set_header_data("Date", 9)
        t.sheet.column_width(9, 160)
        t.geometry("1080x640")
        t.mainloop()
    
    def open_days(self):
        self.log.info("gui.open_days");
        t=gui_table("Days", self.db.get_days())
        t.sheet.set_header_data("Date", 0)
        t.sheet.set_header_data("Entries", 1)
        t.sheet.column_width(1, 64)
        t.sheet.set_header_data("Total", 2)
        t.sheet.set_header_data("Cashed", 3)
        t.sheet.set_header_data("Delta", 4)
        t.geometry("640x320")
        t.mainloop()

    def open_games(self):
        self.log.info("gui.open_games");
        t=gui_table("Games", self.db.get_games())
        t.sheet.set_header_data("Game", 0)
        t.sheet.column_width(0, 200)
        t.sheet.set_header_data("Entries", 1)
        t.sheet.column_width(1, 64)
        t.sheet.set_header_data("Total", 2)
        t.sheet.set_header_data("Cashed", 3)
        t.sheet.set_header_data("Delta", 4)
        t.sheet.set_header_data("ABI", 5)
        t.geometry("640x320")
        t.mainloop()
        
    def edit_config(self):
        self.log.info("gui.config");
        c=gui_config(self.config)

    def open_plot(self):
        plot(0)

class gui_table(tk.Tk):
    def __init__(self, title, data):
        #print(data)
        tk.Tk.__init__(self)
        self.title(title)
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.frame = tk.Frame(self)
        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_rowconfigure(0, weight = 1)
        self.sheet = Sheet(self.frame, data=[list(row) for row in data])
        self.sort_col = 0
        #self.sheet.enable_bindings()
        self.sheet.enable_bindings(("single_select",
                                    "select_all",
                                    #"column_select",
                                    #"row_select",
                                    #"drag_select",
                                    "arrowkeys",
                                    "column_width_resize",
                                    "double_click_column_resize",
                                    "row_height_resize",
                                    "double_click_row_resize",
                                    "right_click_popup_menu",
                                    "rc_select",  # rc = right click
                                    ))

        #self.sheet.extra_bindings("column_select", self.sort_column)
        #self.sheet.extra_bindings("shift_column_select", self.sort_column)   
        self.sheet.bind("<ButtonPress-1>", self.sort_column)
        
        self.frame.grid(row = 0, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")


    def sort_column(self, ev):
        #print("sort column %s" % ev)
        col = self.sheet.MT.identify_col(x=ev.x)
        r = self.sheet.identify_region(ev)
        #print("region %s" % r)
        if r == "header":
            rev = (self.sort_col == col+1)
            self.sheet.set_sheet_data(data = sorted(self.sheet.data, key=lambda cols: cols[col], reverse = rev),
                                      reset_col_positions = False)
            
            if rev:
                self.sort_col = -(col+1)
            else:
                self.sort_col = col+1

class gui_config(tk.Tk):
    def __init__(self, config):        
        tk.Tk.__init__(self)
        self.log = logging.getLogger("starstdb")
        self.log.debug("gui_config.__init__")
        
        self.title("Configuration")
        self.config=config
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        self.frame = tk.Frame(self)
        self.frame.pack()
        f1=tk.Frame(self.frame)
        f1.pack(fill=tk.X)
        f2=tk.Frame(self.frame)
        f2.pack(fill=tk.X)
        f3=tk.Frame(self.frame)
        f3.pack(fill=tk.X)
        f4=tk.Frame(self.frame)
        f4.pack(fill=tk.X)

        l = tk.Label(f1, text='Directory', width=10)
        l.pack(fill=tk.Y, side=tk.LEFT)
        
        self.dir = tk.Entry(f1, width=60)
        self.dir.insert(0, self.config["main"]["dirname"])
        self.dir.pack(fill=tk.Y, side=tk.LEFT)

        l = tk.Label(f2, text='Player', width=10)
        l.pack(fill=tk.Y, side=tk.LEFT)
        self.player = tk.Entry(f2, width=22)
        self.player.insert(0, self.config["main"]["player"])
        self.player.pack(fill=tk.Y, side=tk.LEFT)

        button = tk.Button(f2, text='Check', width=30, command=self.check)
        button.pack(fill=tk.Y, side=tk.RIGHT)
        
        button = tk.Button(f4, text='Cancel', width=30, command=self.destroy)
        button.pack(fill=tk.Y, side=tk.LEFT)
        button = tk.Button(f4, text='Save', width=30, command=self.save)
        button.pack(fill=tk.Y, side=tk.LEFT)


    def save(self):
        self.log.debug("gui.config.save");
        self.log.debug("set dir = %s player %s " % (self.dir.get(), self.player.get()))
        self.config["main"]["dirname"] = self.dir.get()
        self.config["main"]["player"] = self.player.get()
        with open('starstdb.ini', 'w') as configfile:
            self.config.write(configfile)
        self.destroy

    def check(self):
        self.log.debug("gui.config.check dir = %s player %s " % (self.dir.get(), self.player.get()));
        d = self.dir.get()
        p = self.player.get()
        tdir = r"%s\TournSummary\%s" % (d, p)
        hdir = r"%s\HandHistory\%s" % (d, p)

        self.log.info("Base Directory = %s - %s" % (d, ("OK" if os.path.exists(d) else "NOK")))
        self.log.info("Tournament Summary Directory = %s - %s" % (tdir, ("OK" if os.path.exists(tdir) else "NOK")))
        self.log.info("Hand History Directory = %s - %s" % (hdir, ("OK" if os.path.exists(hdir) else "NOK")))
        if os.path.exists(d):
            self.dir.configure(fg = "green4")
        else:
            self.dir.configure(fg = "red4")

        if (os.path.exists(tdir) and os.path.exists(hdir)):
            self.player.configure(fg = "green4")
        else:
            self.player.configure(fg = "red4")

if __name__ == "__main__":
    app = gui("test")
    app.mainloop()
