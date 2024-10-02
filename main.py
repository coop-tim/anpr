from multiprocess import Process

from services.session_manager import SessionManager
from services.api_service import ANPRApiService
from services.repository_service import ANPRRepositoryService

if __name__ == '__main__':
    api_service = ANPRApiService()
    repository = ANPRRepositoryService()
    sm = SessionManager(api_service, repository)
    p = Process(target=sm.monitor, args=())
    p.start()
    p.join()


api_service = ANPRApiService()
repository = ANPRRepositoryService()
sm = SessionManager(api_service, repository)

#result = api_service.get_expired_sessions()
#result = sm._expired_spaces()
#print(result)




#result = sm.session_event(2, 'KM69FHP1')
#print(result)

#api_service = ANPRApiService()

# Session: Id, SpaceId, RegNumber, Started, LastActivity, ReminderStatus, Expired
#result = api_service.create_session(2, 'KM69FHP')
#result = api_service.get_session(2, 'KM69FHP')
#result = api_service.expire_session(2, 'KM69FHP')

# Cameras: Id, SiteId, Location
#result = api_service.upsert_camera(1, 'North-West', 1)

# Spaces: Id, CameraId, Marking, X1, X2, Y1, Y2
#result = api_service.upsert_spaces(3, 'CHARGE2', 10, 100, -400, 40, 2)

# Drivers: Id, Name, Email, Mobile
#result = api_service.upsert_drivers('some name', 'emailaddress', '07737272373', 2)

# Bookings: Id, SpaceId, DriverId, RegNumber, Start, End
#result = api_service.upsert_booking(3, 2, 'ABC1234', '2025-05-29 14:16:00', '2025-05-29 16:16:00', 2)
#print(result)