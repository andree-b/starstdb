from gui import gui, gui_table
from starstdb import starstdb


import configparser
import logging
import sys
log = logging.getLogger("starstdb")
stream = logging.StreamHandler(sys.stdout)
log.addHandler(stream)
log.setLevel(logging.INFO)
import colorer

log.info("Starting starstdb")
log.debug("Version xyz")

config = configparser.ConfigParser()
config.read("starstdb.ini")

if not config.has_section("main"):
    log.warning("Missing config section [main]")
    config.add_section('main')
    
if not config.has_option("main","dirname"):
    log.warning("Missing config option dirname")
    config.set("main", "dirname", ".")

if not config.has_option("main","player"):
    log.warning("Missing config option player")
    config.set("main", "player", "andree_b")
 
# save to file
with open('starstdb.ini', 'w') as configfile:
  config.write(configfile)

db = starstdb()

gui = gui("starstdb", db, config)
gui.mainloop()
