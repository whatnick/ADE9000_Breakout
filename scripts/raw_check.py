f = open(r'c:\Users\tisha\dev\ADE9000_Breakout\ADE9000_Breakout.kicad_sch')
content = f.read()
f.close()

# Find U1 placement
idx = content.find('lib_id "ADE9000_Breakout:ADE9000"')
print('U1 lib_id idx=', idx)
if idx >= 0:
    print(content[idx-10:idx+400])

print()
# Find +3V3 labels to compare
for start in range(len(content)):
    idx2 = content.find('label "+3V3"', start)
    if idx2 < 0:
        break
    print(content[idx2:idx2+80])
    start = idx2 + 1
