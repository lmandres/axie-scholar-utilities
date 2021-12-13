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
                    discordName TEXT,
                    scholarName TEXT NOT NULL,
                    scholarAddress TEXT NOT NULL,
                    scholarPayoutAddress TEXT NOT NULL,
                    scholarPercent REAL,
                    scholarPayout INTEGER,
                    scholarPrivateKey TEXT
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

    def queryDatabase(self, queryIn, paramsIn=None):

        returnList = []

        with sqlite3.connect(self.dbFilePath) as conn:
            cur = conn.cursor()
            rows = None
            if not paramsIn:
                rows = cur.execute(queryIn)
            else:
                rows = cur.execute(queryIn, paramsIn)
            returnList = self.generateQueryReturn(rows)

        return returnList

    def updateDatabaseMany(self, queryIn, queryParamsIn):
        with sqlite3.connect(self.dbFilePath) as conn:
            conn.executemany(queryIn, queryParamsIn)
            conn.commit()

    def getScholarByDiscordName(self, discordName):
        return self.queryDatabase(
            """
                SELECT
                    scholarID,
                    scholarName,
                    scholarAddress,
                    scholarPayoutAddress,
                    scholarPercent,
                    scholarPayout,
                    scholarPrivateKey
                FROM
                    scholars
                WHERE
                    discordName = ?
                ORDER BY
                    scholarID,
                    scholarName
                ;
            """,
            (discordName,)
        )

    def getScholars(self):
        return self.queryDatabase(
            """
                SELECT
                    scholarID,
                    discordName,
                    scholarName,
                    scholarAddress,
                    scholarPayoutAddress,
                    scholarPercent,
                    scholarPayout,
                    scholarPrivateKey
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
                        paramItem["discordName"],
                        paramItem["scholarName"],
                        paramItem["scholarAddress"],
                        paramItem["scholarPayoutAddress"],
                        paramItem["scholarPercent"],
                        paramItem["scholarPayout"],
                        paramItem["scholarPrivateKey"]
                    )
                )
            else:
                updateParams.append(
                    (
                        paramItem["discordName"],
                        paramItem["scholarName"],
                        paramItem["scholarAddress"],
                        paramItem["scholarPayoutAddress"],
                        paramItem["scholarPercent"],
                        paramItem["scholarPayout"],
                        paramItem["scholarPrivateKey"],
                        paramItem["scholarID"],
                    )
                )

        self.updateDatabaseMany(
            """
                INSERT INTO scholars (
                    discordName,
                    scholarName,
                    scholarAddress,
                    scholarPayoutAddress,
                    scholarPercent,
                    scholarPayout,
                    scholarPrivateKey
                ) VALUES (
                    ?,
                    ?,
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
                    discordName = ?,
                    scholarName = ?,
                    scholarAddress = ?,
                    scholarPayoutAddress = ?,
                    scholarPercent = ?,
                    scholarPayout = ?,
                    scholarPrivateKey = ?
                WHERE
                    scholarID = ?
                ;
            """,
            updateParams
        )

    def updateScholarsFromFile(self, paramsDictIn):

        insertParams = []
        updateParams = []

        for paramItem in paramsDictIn:

            scholarID = None

            scholarRows = self.queryDatabase(
                """
                    SELECT
                        scholarID
                    FROM
                        scholars
                    WHERE
                        scholarAddress = ?
                    ;
                """,
                (paramItem["scholarAddress"],)
            )
            if scholarRows:
                scholarID = scholarRows[0]["scholarID"]

            if not scholarID:
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
                        paramItem["scholarPayoutAddress"],
                        paramItem["scholarPercent"],
                        paramItem["scholarPayout"],
                        paramItem["scholarAddress"],
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
                    scholarPayoutAddress = ?,
                    scholarPercent = ?,
                    scholarPayout = ?
                WHERE
                    scholarAddress = ?
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

    def updateTrainersFromFile(self, paramsDictIn):

        insertParams = []
        updateParams = []

        for paramItem in paramsDictIn:

            trainerID = None
            trainerRows = self.queryDatabase(
                """
                    SELECT
                        trainerID
                    FROM
                        trainers
                    WHERE
                        trainerPayoutAddress = ?
                    ;
                """,
                (paramItem["trainerPayoutAddress"],)
            )
            if trainerRows:
                trainerID = trainerRows[0]["trainerID"]

            if not trainerID:
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
                        paramItem["trainerPercent"],
                        paramItem["trainerPayout"],
                        paramItem["trainerPayoutAddress"],
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
                    trainerPercent = ?,
                    trainerPayout = ?
                WHERE
                    trainerPayoutAddress = ?
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

    def updatePaymentsFromFile(self, paramsDictIn):

        insertParams = []

        for paramItem in paramsDictIn:

            scholarID = None
            trainerID = None
            paymentID = None

            scholarRows = self.queryDatabase(
                """
                    SELECT
                        scholarID
                    FROM
                        scholars
                    WHERE
                        scholarAddress = ?
                    ;
                """,
                (paramItem["scholarAddress"],)
            )
            if scholarRows:
                scholarID = scholarRows[0]["scholarID"]

            trainerRows = self.queryDatabase(
                """
                    SELECT
                        trainerID
                    FROM
                        trainers
                    WHERE
                        trainerPayoutAddress = ?
                    ;
                """,
                (paramItem["trainerPayoutAddress"],)
            )
            if trainerRows:
                trainerID = trainerRows[0]["trainerID"]

            paymentParams = (scholarID,)
            paymentWhereClause = "trainerID IS NULL"
            if trainerID:
                paymentParams = (scholarID, trainerID,)
                paymentWhereClause = "trainerID = ?"

            paymentQuery = """
                SELECT
                    paymentID
                FROM
                    payments
                WHERE
                    scholarID = ? AND
                    {}
                ;
            """.format(paymentWhereClause)

            paymentRows = self.queryDatabase(paymentQuery, paymentParams)
            if paymentRows:
                paymentID = paymentRows[0]["paymentID"]

            if not paymentID:
                insertParams.append(
                    (
                        scholarID,
                        trainerID,
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

    def updateSecretsFromFile(self, paramsDictIn):

        updateParams = []

        for paramKey in paramsDictIn.keys():
            paramValue = paramsDictIn[paramKey]
            updateParams.append(
                (
                    paramValue,
                    paramKey,
                )
            )

        self.updateDatabaseMany(
            """
                UPDATE scholars
                SET
                    scholarPrivateKey = ?
                WHERE
                    scholarAddress = ?
                ;
            """,
            updateParams
        )

    def updateTeamInfo(self, teamName="", managerAddress=""):
        self.setSetting("Team Name", teamName)
        self.setSetting("Manager Address", managerAddress)

    def getPaymentsList(self):
        return self.queryDatabase(
            """
                SELECT
                    payments.paymentID,
                    scholars.scholarName,
                    scholars.scholarAddress,
                    scholars.scholarPayout,
                    scholars.scholarPercent,
                    scholars.scholarPayoutAddress,
                    scholars.scholarPrivateKey,
                    trainers.trainerPayoutAddress,
                    trainers.trainerPayout,
                    trainers.trainerPercent
                FROM
                    payments INNER JOIN scholars ON
                        payments.scholarID = scholars.scholarID
                    LEFT OUTER JOIN trainers ON
                        payments.trainerID = trainers.trainerID
                ORDER BY
                    paymentID
                ;
            """
        )
