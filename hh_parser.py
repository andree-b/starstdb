import logging
import glob
import re

class HH_parser:
    h_mark="PokerStars Hand #"
    s_mark="Seat "
    
    def __init__(self, db, config):
        self.log = logging.getLogger("starstdb")
        self.db = db
        self.config = config
        self.log.info("HH_parser init")

    
    def parse_dir(self, dirname):
        self.log.info("parse_dir <%s>" % dirname)
        #tglob=r"""C:\Users\andre\AppData\Local\PokerStars.DE\TournSummary\andree_b\*.txt"""
        self.tglob=dirname + r"""\HH*.txt"""

        for fname in glob.glob(self.tglob):
            self.parse_file(fname)
    

    def parse_file(self, fname):
        self.log.info("Parse <%s>" % fname)
        file = open(fname, mode = 'r', encoding = 'utf-8')
        lines = file.readlines()
        file.close()

        tid = None
        sbounty = 0.0
        cbounty = 0.0
        bounties = 0.0
        first = True
        
        for line in lines:
            if line.startswith(self.h_mark):
                res = r"%s(\d+): Tournament #(\d+), (\S+) (\S+) (.*) - .+ - " % self.h_mark
                #print(res)
                m = re.match(res, line)
                if m is not None:
                    #print(m.groups())
                    tid = int(m.group(2))
                    b = m.group(3).split("+")
                    buyin=float(b[0][1:])
                    if len(b)>2:
                        sbounty=round(float(b[1][1:]),2)
                        rake=round(float(b[2][1:]),2)
                    elif len(b)>1:
                        rake=round(float(b[1][1:]),2)
                    else:
                        rake=0.0                   
                    currency=m.group(4)
                    game = m.group(5)
                    if first:
                        self.log.info("Tid=%d - Buyin: %f - Bounty: %f - Rake %f - Game=%s" % (tid,buyin,sbounty,rake, game))
                        first = False
                    else:
                        self.log.debug("Tid=%d - Buyin: %f - Bounty: %f - Rake %f - Game=%s" % (tid,buyin,sbounty,rake, game))
                else:
                    res = r"%s(\d+): Tournament #(\d+), (\S+) (\S+) (.*) - .+ - " % self.h_mark

            elif line.startswith(self.s_mark):
                res = r"%s(\d+): (.+) \((.* in chips)(, (.*) bounty)\).*" % self.s_mark
                #print(res)
                m = re.match(res, line)
                if m is not None:
                    #print(m.groups())
                    #print("%s - %s" % (m.group(2),self.config["main"]["player"]))
                    if m.group(2)==self.config["main"]["player"]:
                        cbounty = round(float(m.group(5)[1:]),2)
                        #print(cbounty)
            elif line.startswith("%s finished the tournament" % self.config["main"]["player"]):
                if cbounty>sbounty:
                    bounties = bounties + cbounty - sbounty
                    self.log.info("Bounties %f", bounties)
            

        if tid is not None:
            data = self.db.get_tournament(tid)
            if data is None:
                self.log.warn("no tournament data for <%s>" % fname)
            else:
                #print(data)
                if data[4]!=buyin+sbounty:
                    self.log.warn("inconsistent buyin %f != %f + %f <%s>" % (data[4], buyin, sbounty, fname))
                if data[2]!=currency:
                    self.log.warn("inconsistent currency %s != %s <%s>" % (data[2], currency, fname))
                self.db.add_bounty(tid, bounties)
            
        #    data=(tid, game,buyin, rake, currency, startdate,entries, cash)        
        #   self.log.info("Tid=%d - Game=%s - Buyin: %f - Rake %f %s - %s - Entries %d - Cash %f" % data)
        #    self.db.add_tournament(data)
        else:
            self.log.warn("no tournament detected in <%s>" % fname)

