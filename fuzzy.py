from thefuzz import fuzz

def isMatch(str1, str2, threshold = 90):
    return fuzz.ratio(str1, str2) >= threshold