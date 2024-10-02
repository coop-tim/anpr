import time

class SessionManager():
    def __init__(self, api_service, repository):
        self._api_service = api_service
        self._repository = repository

    def _notify(self, name, email, mobile, msg):
        # Should maybe be a new Notification class that can email or text
        print(f'{name}, {msg}')

    def _expired_spaces(self) -> None:
        sessions = self._api_service.get_expired_sessions()
        for s in sessions:
            self._api_service.expire_session(s['SpaceId'], s['RegNumber'])

    def _overdue_sessions(self) -> None:
        sessions = self._api_service.get_overdue_sessions()
        for s in sessions:
            msg = "Your session has ended and is now overdue!"
            self._notify(s['Name'], s['Email'], s['Mobile'], msg)
            self._api_service.set_session_reminder_status(s['SessionId'], 2)

    def _session_ending_reminder(self) -> None:
        sessions_ending = self._api_service.get_sessions_ending()
        for s in sessions_ending:
            msg = "Your current session is ending in 15 mins."
            self._notify(s['Name'], s['Email'], s['Mobile'], msg)
            self._api_service.set_session_reminder_status(s['SessionId'], 1)

    def session_event(self, spaceId, regNumber) -> int:
        # Check for an open session
        session_id = self._api_service.get_session_id(spaceId, regNumber)

        # There is already an active session so just return the id
        if session_id:
            self._api_service.set_session_last_activity(session_id)
            return session_id
        
        # This is a new session
        # Expire any other active sessions for this space or reg
        self._api_service.expire_session(spaceId, regNumber)

        # Create new session
        self._api_service.create_session(spaceId, regNumber)

    def monitor(self):
        while True:
            print('monitoring...')

            # Expire spaces with no activity
            self._expired_spaces()

            # Upcoming Sessions Ending notifications
            self._session_ending_reminder()

            # Session overdue notifications
            self._overdue_sessions()

            time.sleep(5)