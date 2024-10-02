import time
import fuzzy
import uk_numplate_regex
import anpr
from services.api_service import ANPRApiService
from services.repository_service import ANPRRepositoryService
from services.session_manager import SessionManager
import asyncio

repo = ANPRRepositoryService()
api = ANPRApiService(repo)
sessionManager = SessionManager(api, repo)

#Get camera details
cameraId = api.upsert_camera(1, "Round the back of the shop", 1)
camera = {
    "id": cameraId,
    "spaces": {}
}
spaceId = api.upsert_spaces(cameraId, 'CHARGE1', 10, 100, -400, 40, 1)
camera["spaces"][spaceId] = {
    "spaceId": spaceId,
    "top": 0,
    "left": 0,
    "right": 600,
    "bottom": 600,
    "currentSession": None
}
spaceId = api.upsert_spaces(cameraId, 'CHARGE2', 10, 100, -400, 40, 2)
camera["spaces"][spaceId] = {
    "spaceId": spaceId,
    "top": 0,
    "left": 0,
    "right": 600,
    "bottom": 600,
    "currentSession": None
}

currentSession = None
reg = None

def getBooking(spaceId, time):
    print("Get booking for space ", spaceId, " at ", time)
    #TODO
    return {
        "id": 1,
        "spaceId": 1,
        "reg": "SF16GFM"
    }

def startSession(reg, booking):
    print("Start session for ", reg)
    sessionId = sessionManager.session_event(booking["spaceId"], reg)
    return {
        "id": sessionId,
        "bookingId": booking,
        "spaceId": booking["spaceId"],
        "reg": reg
    }

def endSession(session):
    print("End session for ", session["reg"])
    #TODO
    api.expire_session(session["spaceId"], session["reg"])
    return None

def logSnapshot(reg, session):
    print("Continue session for ", reg)
    sessionId = sessionManager.session_event(session["spaceId"], reg)
    return {
        "id": sessionId,
        "bookingId": session["bookingId"],
        "spaceId": session["spaceId"],
        "reg": reg
    }

def checkSession(session):
    #TODO
    return session

#Enter snapshot loop

spaces = camera["spaces"]

def takeSnapshot():
    print("Taking snapshot")
    
    registrations = asyncio.run(anpr.getRegInSpaces(camera))

    for spaceId in registrations:
        space = spaces[spaceId]
        currentSession = space["currentSession"]
        spaceSnapshot = registrations[spaceId]
        reg = spaceSnapshot["reg"]
        spaceId = spaceSnapshot["spaceId"]
        print("Reg in space ", spaceId, ": ", reg)
        if currentSession == None:
            if reg == None:
                continue;
            
            #Get booking
            booking = getBooking(spaceId, time.time)
            if booking != None:
                print("Booking found: ", booking["id"])
                if fuzzy.isMatch(booking['reg'], reg):
                    reg = booking['reg']
                    currentSession = space["currentSession"] = startSession(reg, booking)
                    continue;
                else:
                    print("Reg does not match booking")
                    if uk_numplate_regex.isUkNumberplate(reg):
                        currentSession = space["currentSession"] = startSession(reg, booking);
                        # alerting handled by central db
                    else:
                        print("Invalid reg: ", reg)
                        continue;
            else:
                print("No booking found")
                if uk_numplate_regex.isUkNumberplate(reg):
                        currentSession = space["currentSession"] = startSession(reg, None);
                        # alerting handled by central db
                else:
                    print("Invalid reg: ", reg)
                    continue;
        else :
            if reg == None:
                # Session ending will be handled by central db, 
                # here we check if the session has ended
                currentSession = space["currentSession"] = checkSession(currentSession)
                continue;
            if fuzzy.isMatch(currentSession['reg'], reg):
                reg = currentSession['reg']
                logSnapshot(reg, currentSession)
                #overstay and alerting logic handled by central db
            else:
                newBooking = getBooking(spaceId, time.time)
                if newBooking != None:
                    print("Booking found: ", newBooking["id"])
                    if fuzzy.isMatch(newBooking['reg'], reg):
                        reg = newBooking['reg']
                        currentSession = space["currentSession"]= endSession(currentSession)
                        currentSession = space["currentSession"] = startSession(reg, newBooking)
                        continue;
                    else:
                        print("Reg does not match booking")
                        if uk_numplate_regex.isUkNumberplate(reg):
                            currentSession  = space["currentSession"]= endSession(currentSession)
                            currentSession  = space["currentSession"]= startSession(reg, newBooking)
                            # alerting handled by central db
                        else:
                            print("Invalid reg: ", reg)
                            currentSession  = space["currentSession"]= endSession(currentSession)
                            continue;
                else:
                    if fuzzy.isMatch(newBooking['reg'], reg):
                        reg = newBooking['reg']
                        currentSession = space["currentSession"] = endSession(currentSession)
                        currentSession = space["currentSession"] = startSession(reg, newBooking)
                        continue;
                    else:
                        print("Unexpected reg: ", reg, " expected ", newBooking['reg'])
                        if uk_numplate_regex.isUkNumberplate(reg):
                            currentSession  = space["currentSession"]= endSession(currentSession)
                            currentSession  = space["currentSession"]= startSession(reg, newBooking)
                            # alerting handled by central db
                        else:
                            print("Invalid reg: ", reg)
                            currentSession  = space["currentSession"]= endSession(currentSession)
                            continue;
            continue;

takeSnapshot()
while(True):
    time.sleep(5)
    takeSnapshot()