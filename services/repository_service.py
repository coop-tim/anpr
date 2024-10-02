import sqlite3

class ANPRRepositoryService:
    def __init__(self, recreate=False):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        
        self._conn = sqlite3.connect(f'anpr.db')
        self._conn.row_factory = dict_factory
        self._cur = self._conn.cursor()

        if recreate:
            self._drop_tables()
            self._create_tables()

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _create_tables(self):
        self._cur.execute("CREATE TABLE IF NOT EXISTS Camera(Id INTEGER PRIMARY KEY, SiteId, Location)")
        self._cur.execute("CREATE TABLE IF NOT EXISTS Spaces(Id INTEGER PRIMARY KEY, CameraId, Marking, X1, X2, Y1, Y2)")
        self._cur.execute("CREATE TABLE IF NOT EXISTS Drivers(Id INTEGER PRIMARY KEY, Name, Email, Mobile)")
        self._cur.execute("CREATE TABLE IF NOT EXISTS Bookings(Id INTEGER PRIMARY KEY, SpaceId, DriverId, RegNumber, Start, End)")
        self._cur.execute("CREATE TABLE IF NOT EXISTS Session(Id INTEGER PRIMARY KEY, SpaceId, RegNumber, Started, LastActivity, ReminderStatus, Expired)")
        self._conn.commit()

    def _drop_tables(self, table=None):
        tables = [table] if table else ['Camera', 'Session', 'Spaces', 'Drivers', 'Bookings']

        for table in tables:
            self._cur.execute(f"DROP TABLE IF EXISTS {table}")

        self._conn.commit()

    def execute(self, sql):
        result = self._cur.execute(sql)
        self._conn.commit()
        return result
    
    def executemany(self, sql, data):
        result = self._cur.executemany(sql, data)
        self._conn.commit()
        return result