import re

pattern = r"(^[A-Z]{2}[0-9]{2}\s?[A-Z]{3}$)|(^[A-Z][0-9]{1,3}[A-Z]{3}$)|(^[A-Z]{3}[0-9]{1,3}[A-Z]$)|(^[0-9]{1,4}[A-Z]{1,2}$)|(^[0-9]{1,3}[A-Z]{1,3}$)|(^[A-Z]{1,2}[0-9]{1,4}$)|(^[A-Z]{1,3}[0-9]{1,3}$)|(^[A-Z]{1,3}[0-9]{1,4}$)|(^[0-9]{3}[DX]{1}[0-9]{3}$)"
prog = re.compile(pattern)
print(prog.match("test") != None)
numplates = ["AB12 CDE",
"CD34 EFG",
"EF56 GHI",
"GH68 JKL",
"JH19 KLM",
"LM20 NOP",
"PQ21 RST",
"VW22 XYZ",
"XY23 ABC",
"YZ24 DEF"]

for plate in numplates:
    print(prog.match(plate) != None)
