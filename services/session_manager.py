import time

class SessionManager():
    def __init__(self, api_service, repository):
        self._api_service = api_service
        self._repository = repository

    def session_event(self, spaceId, regNumber) -> int:
        # Check for an open session
        session_id = self._api_service.get_session(spaceId, regNumber)

        # There is already an active session so just return the id
        if session_id:
            return session_id[0]
        
        # This is a new session
        # Expire any other active sessions for this space or reg
        self._api_service.expire_session(spaceId, regNumber)

        # Create new session
        self._api_service.create_session(spaceId, regNumber)

    def monitor(self):
        while True:
            print('monitoring...')

            time.sleep(5)