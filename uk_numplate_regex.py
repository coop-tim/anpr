import re

pattern = r"(^[A-Z]{2}[0-9]{2}\s?[A-Z]{3}$)|(^[A-Z][0-9]{1,3}[A-Z]{3}$)|(^[A-Z]{3}[0-9]{1,3}[A-Z]$)|(^[0-9]{1,4}[A-Z]{1,2}$)|(^[0-9]{1,3}[A-Z]{1,3}$)|(^[A-Z]{1,2}[0-9]{1,4}$)|(^[A-Z]{1,3}[0-9]{1,3}$)|(^[A-Z]{1,3}[0-9]{1,4}$)|(^[0-9]{3}[DX]{1}[0-9]{3}$)"
ukPlateRegex = re.compile(pattern)

def isUkNumberplate(str):
    return ukPlateRegex.match(str) != None

def cleanAnpr(str):
    # we never have letter I or Q(rarely) in a UK EV plate
    str = str.replace("I", "1")
    str = str.replace("i", "1")
    str = str.replace("Q", "O")
    
    # return early if its now valid
    if isUkNumberplate(str):
        return str

    # if the string is not 7 chars long it could be a 'cherished' plate number
    if len(str) != 7:
        return str
    
    # replace letters that may have been mistaken with their closest
    # numeric equivalents, for the numeric portion of the plate format
    old = str
    str = replaceCharsAt(str, ['i','I','l','L'], '1', [2,3])
    str = replaceCharsAt(str, ['B'], '8', [2,3])
    str = replaceCharsAt(str, ['A'], '4', [2,3])
    str = replaceCharsAt(str, ['O', 'o'], '0', [2,3])

    #only return it if its actually now valid
    if isUkNumberplate(str):
        return str
    else:
        return old

def replaceCharsAt(str, chars, replace, indices):
    for index in indices:
        for char in chars:
            if str[index] == char:
                str = str[:index] + replace + str[index + 1:]
    return str