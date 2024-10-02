from datetime import datetime, timedelta

from services.repository_service import ANPRRepositoryService

class ANPRApiService:
    def __init__(self):
        self._repository = ANPRRepositoryService()

    def _insert_one(self, table, sql) -> int:
        self._repository.execute(sql)
        result = self._repository.execute(f'SELECT MAX(Id) FROM {table}')
        id = result.fetchone()
        return id[0]
    
    def _upsert(self, table, sql, id=None) -> int:
        if id:
            self._repository.execute(sql)
            return id
        
        return self._insert_one(table, sql)
    
    # Bookings
    def upsert_booking(self, space_id, driver_id, reg, start, end, booking_id=None) -> int:
        if booking_id:
            sql = f"UPDATE Bookings SET SpaceId = {space_id}, DriverId = {driver_id}, RegNumber = '{reg}', Start = datetime('{start}'), End = datetime('{end}') WHERE Id = {booking_id}"
        else:
            sql = f"INSERT INTO Bookings (SpaceId, DriverId, RegNumber, Start, End) VALUES ({space_id}, {driver_id}, '{reg}', datetime('{start}'), datetime('{end}'))"

        return self._upsert('Bookings', sql, id=booking_id)
    
    # Camera
    def upsert_camera(self, site_id, location, camera_id=None) -> int:
        if camera_id:
            sql = f"UPDATE Camera SET SiteId = {site_id}, Location = '{location}' WHERE Id = {camera_id}"
        else:
            sql = f"INSERT INTO Camera (SiteId, Location) VALUES ({site_id}, '{location}')"

        return self._upsert('Camera', sql, id=camera_id)
    
    # Driver
    def get_driver_contact_details(self, reg) -> dict:
        # todo: Might be possible to have multiple drivers assigned to a car
        result = self._repository.execute(f"SELECT Name, Email, Mobile FROM Drivers WHERE RegNumber = '{reg}'")
        return result.fetchone()

    def upsert_drivers(self, name, email, mobile, driver_id=None) -> int:
        if driver_id:
            sql = f"UPDATE Drivers SET Name = '{name}', Email = '{email}', Mobile = '{mobile}' WHERE Id = {driver_id}"
        else:
            sql = f"INSERT INTO Drivers (Name, Email, Mobile) VALUES ('{name}', '{email}', '{mobile}')"

        return self._upsert('Drivers', sql, id=driver_id)

    # Session
    def create_session(self, spaceId, reg) -> int:
        sql = f"INSERT INTO Session (SpaceId, RegNumber, Started, LastActivity, ReminderStatus, Expired) VALUES ({spaceId}, '{reg}', datetime(), datetime(), 0, 0)"
        return self._insert_one('Session', sql)
    
    def get_expired_sessions(self) -> list:
        dt = (datetime.utcnow()+timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
        result = self._repository.execute(f"SELECT Id, SpaceId, RegNumber FROM Session WHERE Expired = 0 AND LastActivity <= datetime('{dt}')")
        return result.fetchall() 
    
    def get_overdue_sessions(self) -> list:
        pass

    def get_sessions_ending(self) -> list:
        dt = (datetime.utcnow()+timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        result = self._repository.execute(f"SELECT s.Id as SessionId FROM Bookings b JOIN Session s ON s.RegNumber = b.RegNumber AND s.SpaceId = b.SpaceId JOIN Drivers d ON d.Id = b.DriverId WHERE Expired = 0 AND End <= datetime('{dt}')")
        return result.fetchall() 

    def get_session_id(self, spaceId, regNumber) -> int:
        result = self._repository.execute(f"SELECT Id FROM Session WHERE SpaceId = {spaceId} AND RegNumber = '{regNumber}'")
        session_id = result.fetchone()
        return session_id[0] if session_id else None
    
    def expire_session(self, spaceId, regNumber) -> None:
        self._repository.execute(f"UPDATE Session SET Expired = 1 WHERE (SpaceId = {spaceId} AND RegNumber = '{regNumber}') AND Expired = 0")

    def set_session_last_activity(self, id):
        self._repository.execute(f"UPDATE Session SET LastActivity = datetime() WHERE Id = {id}")

    def set_session_reminder_status(self, id, status):
        self._repository.execute(f"UPDATE Session SET ReminderStatus = {status} WHERE SpaceId = {id}")

    # Space
    def get_space_id(self, marking) -> int:
        result = self._repository.execute(f"SELECT Id FROM Space WHERE Marking = '{marking}'")
        space_id = result.fetchone()
        return space_id[0] if space_id else None
    
    def upsert_spaces(self, camera_id, marking, x1, x2, y1, y2, space_id=None) -> int:
        if space_id:
            sql = f"UPDATE Spaces SET CameraId = {camera_id}, Marking = '{marking}', X1 = {x1}, X2 = {x2}, Y1 = {y1}, Y2 = {y2} WHERE Id = {space_id}"
        else:
            sql = f"INSERT INTO Spaces (CameraId, Marking, X1, X2, Y1, Y2) VALUES ({camera_id}, '{marking}', {x1}, {x2}, {y1}, {y2})"

        return self._upsert('Spaces', sql, id=space_id)
