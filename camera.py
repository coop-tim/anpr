import time
import fuzzy
import uk_numplate_regex
import anpr

#Get camera details
camera = {
    "id": 1,
    "spaces":
        {
            1:
            {
                "spaceId": 1,
                "top": 0,
                "left": 0,
                "right": 600,
                "bottom": 600,
                "currentSession": None
            },
            2: {
                "spaceId": 2,
                "top": 0,
                "left": 0,
                "right": 600,
                "bottom": 600,
                "currentSession": None
            }
            
        }
    
}

currentSession = None
reg = None

def getBooking(spaceId, time):
    print("Get booking for space ", spaceId, " at ", time)
    return {
        "id": 1,
        "reg": "SF16GFM"
    }

def startSession(reg, booking):
    print("Start session for ", reg)
    return {
        "id": 1,
        "bookingId": booking,
        "spaceId": 1,
        "reg": reg
    }

def endSession(session):
    print("End session for ", session["reg"])
    return None

def logSnapshot(reg, session):
    print("Continue session for ", reg)
    return

def checkSession(session):
    return session

#Enter snapshot loop

spaces = camera["spaces"]

while(True):
    time.sleep(5)
    print("Taking snapshot")
    
    registrations = anpr.getRegInSpaces(camera)

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