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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    paymentID INTEGER PRIMARY KEY AUTOINCREMENT,
                    scholarID INTEGER NOT NULL,
                    trainerID INTEGER
                );
            """)
            conn.commit()

    def setSetting(self, settingName, settingValue):

        with sqlite3.connect(self.dbFilePath) as conn:

            row = conn.execute(
                "SELECT COUNT(*) FROM settings WHERE settingName = ?;",
                [settingName]
            ).fetchone()
            if not row[0]:
                conn.execute(
                    """
                        INSERT INTO settings (
                            settingName,
                            settingValue
                        ) VALUES (
                            ?, ?
                        );
                    """,
                    (settingName, settingValue,)
                )
            else:
                conn.execute(
                    """
                        UPDATE settings
                        SET
                            settingValue = ?
                        WHERE
                            settingName = ?
                        ;
                    """,
                    (settingValue, settingName,)
                )
            conn.commit()

    def getSetting(self, settingName):
        returnValue = None
        with sqlite3.connect(self.dbFilePath) as conn:
            row = conn.execute(
                "SELECT settingValue FROM settings WHERE settingName = ?;",
                [settingName]
            ).fetchone()
            if row:
                returnValue = row[0]
        return returnValue

    def generateQueryReturn(self, rowsIn):

        returnList = []

        for row in rowsIn:
            newDict = {}
            for colIndex in range(0, len(rowsIn.description), 1):
                newDict[rowsIn.description[colIndex][0]] = row[colIndex]
            returnList.append(newDict)

        return returnList

    def queryDatabase(self, queryIn):

        returnList = []

        with sqlite3.connect(self.dbFilePath) as conn:
            cur = conn.cursor()
            rows = cur.execute(queryIn)
            returnList = self.generateQueryReturn(rows)

        return returnList

    def updateDatabaseMany(self, queryIn, queryParamsIn):
        with sqlite3.connect(self.dbFilePath) as conn:
            conn.executemany(queryIn, queryParamsIn)
            conn.commit()

    def getScholars(self):
        return self.queryDatabase(
            """
                SELECT
                    scholarID,
                    scholarName,
                    scholarAddress,
                    scholarPayoutAddress,
                    scholarPercent,
                    scholarPayout
                FROM
                    scholars
                ORDER BY
                    scholarID,
                    scholarName
                ;
            """
        )

    def updateScholars(self, paramsDictIn):

        insertParams = []
        updateParams = []

        for paramItem in paramsDictIn:
            if not paramItem["scholarID"]:
                insertParams.append(
                    (
                        paramItem["scholarName"],
                        paramItem["scholarAddress"],
                        paramItem["scholarPayoutAddress"],
                        paramItem["scholarPercent"],
                        paramItem["scholarPayout"],
                    )
                )
            else:
                updateParams.append(
                    (
                        paramItem["scholarName"],
                        paramItem["scholarAddress"],
                        paramItem["scholarPayoutAddress"],
                        paramItem["scholarPercent"],
                        paramItem["scholarPayout"],
                        paramItem["scholarID"],
                    )
                )

        self.updateDatabaseMany(
            """
                INSERT INTO scholars (
                    scholarName,
                    scholarAddress,
                    scholarPayoutAddress,
                    scholarPercent,
                    scholarPayout
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                );
            """,
            insertParams
        )
        self.updateDatabaseMany(
            """
                UPDATE scholars
                SET
                    scholarName = ?,
                    scholarAddress = ?,
                    scholarPayoutAddress = ?,
                    scholarPercent = ?,
                    scholarPayout = ?
                WHERE
                    scholarID = ?
                ;
            """,
            updateParams
        )

    def deleteScholars(self, paramsDictIn):

        deleteParams = []

        for paramItem in paramsDictIn:
            if paramItem["scholarID"]:
                deleteParams.append((paramItem["scholarID"],))
        
        self.updateDatabaseMany(
            """
                DELETE
                FROM
                    scholars
                WHERE
                    scholarID = ?
                ;
            """,
            deleteParams
        )

    def getTrainers(self):
        return self.queryDatabase(
            """
                SELECT
                    trainerID,
                    trainerName,
                    trainerPayoutAddress,
                    trainerPercent,
                    trainerPayout
                FROM
                    trainers
                ORDER BY
                    trainerID,
                    trainerName
                ;
            """
        )

    def updateTrainers(self, paramsDictIn):

        insertParams = []
        updateParams = []

        for paramItem in paramsDictIn:
            if not paramItem["trainerID"]:
                insertParams.append(
                    (
                        paramItem["trainerName"],
                        paramItem["trainerPayoutAddress"],
                        paramItem["trainerPercent"],
                        paramItem["trainerPayout"],
                    )
                )
            else:
                updateParams.append(
                    (
                        paramItem["trainerName"],
                        paramItem["trainerPayoutAddress"],
                        paramItem["trainerPercent"],
                        paramItem["trainerPayout"],
                        paramItem["trainerID"],
                    )
                )

        self.updateDatabaseMany(
            """
                INSERT INTO trainers (
                    trainerName,
                    trainerPayoutAddress,
                    trainerPercent,
                    trainerPayout
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    ?
                );
            """,
            insertParams
        )
        self.updateDatabaseMany(
            """
                UPDATE trainers
                SET
                    trainerName = ?,
                    trainerPayoutAddress = ?,
                    trainerPercent = ?,
                    trainerPayout = ?
                WHERE
                    trainerID = ?
                ;
            """,
            updateParams
        )

    def deleteTrainers(self, paramsDictIn):

        deleteParams = []

        for paramItem in paramsDictIn:
            if paramItem["trainerID"]:
                deleteParams.append((paramItem["trainerID"],))
        
        self.updateDatabaseMany(
            """
                DELETE
                FROM
                    trainers
                WHERE
                    trainerID = ?
                ;
            """,
            deleteParams
        )

    def getPayments(self):
        return self.queryDatabase(
            """
                SELECT
                    paymentID,
                    scholarID,
                    trainerID
                FROM
                    payments
                ORDER BY
                    paymentID
                ;
            """
        )

    def updatePayments(self, paramsDictIn):

        insertParams = []
        updateParams = []

        for paramItem in paramsDictIn:
            if not paramItem["paymentID"]:
                insertParams.append(
                    (
                        paramItem["scholarID"],
                        paramItem["trainerID"],
                    )
                )
            else:
                updateParams.append(
                    (
                        paramItem["scholarID"],
                        paramItem["trainerID"],
                        paramItem["paymentID"],
                    )
                )

        self.updateDatabaseMany(
            """
                INSERT INTO payments (
                    scholarID,
                    trainerID
                ) VALUES (
                    ?,
                    ?
                );
            """,
            insertParams
        )
        self.updateDatabaseMany(
            """
                UPDATE payments
                SET
                    scholarID = ?,
                    trainerID = ?
                WHERE
                    paymentID = ?
                ;
            """,
            updateParams
        )

    def deletePayments(self, paramsDictIn):

        deleteParams = []

        for paramItem in paramsDictIn:
            if paramItem["paymentID"]:
                deleteParams.append((paramItem["paymentID"],))
        
        self.updateDatabaseMany(
            """
                DELETE
                FROM
                    payments
                WHERE
                    paymentID = ?
                ;
            """,
            deleteParams
        )

    def updateTeamInfo(self, teamName="", managerAddress=""):
        self.setSetting("Team Name", teamName)
        self.setSetting("Manager Address", managerAddress)