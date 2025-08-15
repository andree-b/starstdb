import sqlite3
import logging

class starstdb:

    ALL_GAMES = "all games"

    def add_tournament(self, data):
        sql = ''' SELECT * FROM TOURNAMENTS WHERE Tid=%d ; ''' % data[0]
        #print(sql)
        self.cursor_obj.execute(sql, ())
        if self.cursor_obj.fetchone() is None:        
            sql = ''' INSERT INTO TOURNAMENTS(Tid,Game,Buyin,Rake,Currency,StartDate,Entries,Cash,Bounties)
                  VALUES(?,?,?,?,?,?,?,?,0.0) '''
            self.log.info("New tournament #%d" % data[0])
        else:
            sql = ''' UPDATE TOURNAMENTS SET Tid=?,Game=?,Buyin=?,Rake=?,Currency=?,StartDate=?,Entries=?,Cash=?
                  WHERE Tid=%d ''' % data[0]
            self.log.info("Updating tournament #%d" % data[0])

        #print(sql)    
        self.cursor_obj.execute(sql, data)
        self.connection_obj.commit()
        return self.cursor_obj.lastrowid

    def add_bounty(self, tid, bounty):
        sql = ''' UPDATE TOURNAMENTS SET Bounties=?
                  WHERE Tid=%d ''' % tid
        self.log.info("Updating bounties for tournament #%d" % tid)

        #print(sql)    
        self.cursor_obj.execute(sql, [bounty])
        self.connection_obj.commit()
        return self.cursor_obj.lastrowid

    def reset_tables(self, drop=True):
        # Drop the  table if already exists.
        if drop:
            self.cursor_obj.execute("DROP TABLE IF EXISTS TOURNAMENTS")
            self.cursor_obj.execute("DROP TABLE IF EXISTS STATS")
            self.cursor_obj.execute("DROP TABLE IF EXISTS PLAYERS")
          
        # Creating tables
        # main tournaments table:
        table = """ CREATE TABLE if not exists TOURNAMENTS (
                    Iid INTEGER PRIMARY KEY,
                    Tid UNSIGNED BIG INT NOT NULL,
                    Game CHAR(80),
                    Buyin REAL,
                    Rake REAL,
                    Cash REAL,
                    Bounties REAL,
                    Currency CHAR(8),
                    Entries INT,
                    StartDate DATE
                ); """        
        self.cursor_obj.execute(table)   

        # players table:
        table = """ CREATE TABLE if not exists PLAYERS (
                    Pid INTEGER PRIMARY KEY,
                    Name CHAR(80),
                    Country CHAR(25),
                    Hands INT
                ); """

        self.cursor_obj.execute(table)   


        # stats table:
        table = """ CREATE TABLE if not exists STATS (
                    Sid INTEGER PRIMARY KEY,
                    Player INTEGER,
                    Game CHAR(80),
                    Hands INT,
                    VPIP INT,
                    CBET INT,
                    TBET INT,
                    F3B INT,
                    FOREIGN KEY (Player) REFERENCES PLAYERS (Pid)
                ); """

        self.cursor_obj.execute(table)   



        print("Tables are Ready")
    
    def __init__(self):
        self.log = logging.getLogger("starstdb")

        # Connecting to sqlite
        # connection object
        self.connection_obj = sqlite3.connect('starstdb.db')
        #self.connection_obj.execute("PRAGMA foreign_keys = on")
         
        # cursor object
        self.cursor_obj = self.connection_obj.cursor()
        self.reset_tables(False)
         

    def __del__(self):    
        # Close the connection
        self.connection_obj.close()

    def get_tournament(self, tid):
        self.log.info("db.get_tournament #%d" % tid)
        sql = """ SELECT Tid,Game,Currency,(Buyin+Rake)*Entries,Buyin,Rake,Entries,Cash,StartDate FROM TOURNAMENTS WHERE Tid=%d; """ % tid
        self.cursor_obj.execute(sql)
        row = self.cursor_obj.fetchone()
        return row

    def get_players(self):
        self.log.info("db.get_players")
        sql = """ SELECT * FROM PLAYERS; """
        self.cursor_obj.execute(sql)
        rows = self.cursor_obj.fetchall()
        
        for row in rows:
            self.log.info(row)
        return rows

    def get_tournaments(self, game=ALL_GAMES):
        self.log.info("db.get_tournaments %s " % game)
        if game != self.ALL_GAMES:
            w = " WHERE Game='%s'" % game
        else:
            w = ""
        sql = """ SELECT Tid,Game,Currency,(Buyin+Rake)*Entries,Buyin,Rake,Entries,Cash,Bounties,StartDate FROM TOURNAMENTS%s; """ % w
        self.log.info(sql)
        #LEFT JOIN PLAYERS P ON T.Uid = P.Uid;
        self.cursor_obj.execute(sql)
        rows = self.cursor_obj.fetchall()
        for row in rows:
            self.log.debug(row)
        return rows

    def get_days(self, game=ALL_GAMES):
        self.log.info("db.get_days %s" % game)
        if game != self.ALL_GAMES:
            w = " WHERE Game='%s'" % game
        else:
            w = ""
        
        sql = """ SELECT S.SDate, S.E, S.B, S.C, Round((S.C - S.B),2)
                    FROM (SELECT
                            substr(StartDate,1,10) as SDate,
                            SUM(Entries) as E,
                            ROUND(SUM((Buyin+Rake)*Entries),2) as B,
                            ROUND(SUM(Cash+Bounties),2) as C
                         FROM TOURNAMENTS%s Group By SDate) S; """ %w

        self.log.info(sql)
        self.cursor_obj.execute(sql)
        rows = self.cursor_obj.fetchall()
        
        for row in rows:
            self.log.debug(row)
        return rows

    def get_games(self):
        self.log.info("db.get_games")
        sql = """ SELECT S.G, S.E, S.B, S.C, Round((S.C - S.B),2),S.ABI
                    FROM (SELECT
                            Game as G,
                            SUM(Entries) as E,
                            ROUND(SUM((Buyin+Rake)*Entries),2) as B,
                            ROUND(SUM(Cash+Bounties),2) as C,
                            ROUND(SUM((Buyin+Rake)*Entries)/SUM(Entries),2) as ABI
                            FROM TOURNAMENTS Group By Game) S; """
        self.cursor_obj.execute(sql)
        rows = self.cursor_obj.fetchall()
        
        for row in rows:
            self.log.debug(row)
        return rows

