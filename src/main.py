from countries import countries


l = 0
for country in countries:
    if l == 4:
        break
    print(country["code"])
    l += 1
