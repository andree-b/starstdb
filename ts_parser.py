import logging
import glob
import re

def r2(s):
    return round(float(s.replace(',','')),2)

class TS_parser:
    t_mark="PokerStars Tournament #"
    b_mark="Buy-In: "
    s_mark="Tournament started "
    r_mark="You made "
    ticket="Tournament Ticket"
    qualify="(qualified for the target tournament"
    target="Target Tournament"
    still="still playing"

    
    def __init__(self, db, config):
        self.log = logging.getLogger("starstdb")
        self.db = db
        self.config = config
        self.log.info("TS_parser init")

    
    def parse_dir(self, dirname):
        self.log.info("parse_dir <%s>" % dirname)
        self.tglob=dirname + r"""\*.txt"""

        for fname in glob.glob(self.tglob):
            self.parse_file(fname)
    

    def parse_file(self, fname):
        self.log.info("Parse <%s>" % fname)
        file = open(fname, mode = 'r', encoding = 'utf-8')
        lines = file.readlines()
        file.close()

        tid = None
        entries = 1
        cash = 0.0
        qcost = 0.0
        
        for line in lines:
            if line.startswith(self.t_mark):
                f = line[len(self.t_mark):].split(',')
                tid=int(f[0])
                game=f[1].strip()
                self.log.debug("Tid=%d - Game=%s" % (tid, game))

            elif line.startswith(self.b_mark):
                f = line.split()
                currency=f[2]
                b = f[1].split('/')

                buyin=r2(b[0][1:])
                if len(b)>1:
                    rake=r2(b[1][1:])
                else:
                    rake=0.0
                self.log.debug("Buyin: %f - Rake %f" % (buyin, rake))


            elif line.startswith(self.s_mark):
                f = line[len(self.s_mark):].split(' [')
                startdate = f[0].strip()
                
            elif line.startswith(self.r_mark):
                f = line.split(' ')
                e = int(f[2])
                entries=1+e
                t = float(f[8].strip()[1:-1])
                if round((t / e),2) != round(rake+buyin, 2):
                    self.log.warn("re-entry cost is not multiple of buyin")
                self.log.info("Re-Entries %d @ %f" % (e, t))

##            elif re.match("^ *[0-9]+: %s .*" % self.config["main"]["player"], line):                
##                #print(line)
##                f = line.split(',')
##                e = f[1].strip().split('(')
##                print(e)
##                c = 0.0
##                if len(e)>1:
##                    if e[0].startswith(self.ticket):
##                        t = e[1].strip().split("$")
##                        #print(t)
##                        tv = t[1].split(" ")
##                        #print(tv)
##                        c = round(float(tv[0]),2)
##                    elif e[1].startswith(self.qualify):
##                        #print("qualified")
##                        c = qcost
##                    else:
##                        c = round(float(e[0][1:]),2)
##                                
##                cash = cash + c
##                self.log.info("Cash %f - %f " % (c, cash))
            elif (m := re.match(r"^ *[0-9]+: %s .*, +((\S+).*)?" % self.config["main"]["player"], line)) is not None:
                print(m)
                c = 0.0
                if m[1] is not None:
                    print(m.groups())    
                    if m[1].startswith(self.ticket):
                        t = m[0].strip().split("$")
                        print(t)
                        tv = t[1].split(" ")
                        print(tv)
                        c = round(float(tv[0]),2)
                    elif m[1].startswith(self.qualify):
                        print("qualified")
                        c = qcost
                    elif m[1].startswith(self.still):
                        print("still playing")
                    elif m[2] is not None:
                        c = r2(m[2][1:])
                    cash = cash + c
                    self.log.info("Cash %f - %f " % (c, cash))
                        
            elif line.startswith(self.target):
                f = line.split('$')
                if len(f)>1:
                    e = f[1].strip().split(' ')
                    qcost = r2(e[0])
                    self.log.info("Target cost %f" % (qcost))
                else:
                    self.log.warn("Target without cost!? %s" % (line))

        if tid is not None:
            data=(tid, game,buyin, rake, currency, startdate,entries, cash)        
            self.log.info("Tid=%d - Game=%s - Buyin: %f - Rake %f %s - %s - Entries %d - Cash %f" % data)
            self.db.add_tournament(data)
        else:
            self.log.warn("no tournament detected in <%s>" % fname)
