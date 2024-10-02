from thefuzz import fuzz

def isMatch(str1, str2, threshold = 90):
    ratio = fuzz.ratio(str1, str2)
    print("Fuzzy match ratio ", ratio)
    return ratio >= threshold