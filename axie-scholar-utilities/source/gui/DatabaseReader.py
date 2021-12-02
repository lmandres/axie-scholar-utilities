import sqlite3


class DatabaseReader(object):

    dbFilePath = ""

    def __init__(self, dbFilePathIn=""):
        self.dbFilePath = dbFilePathIn

    def createDatabaseTables(self):

        with sqlite3.connect(self.dbFilePath) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    settingID INTEGER PRIMARY KEY AUTOINCREMENT,
                    settingName TEXT NOT NULL,
                    settingValue TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scholars (
                    scholarID INTEGER PRIMARY KEY AUTOINCREMENT,
                    scholarName TEXT NOT NULL,
                    scholarAddress TEXT NOT NULL,
                    scholarPayoutAddress TEXT NOT NULL,
                    scholarPercent REAL,
                    scholarPayout INTEGER
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trainers (
                    trainerID INTEGER PRIMARY KEY AUTOINCREMENT,
                    trainerName TEXT NOT NULL,
                    trainerPayoutAddress TEXT NOT NULL,
                    trainerPercent REAL,
                    trainerPayout INTEGER
                );
            """)
            conn.commit()

    def updateTeamInfo(
        self,
        teamName="",
        managerAddress=""
    ):
         
        
