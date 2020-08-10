w = open("last_index.txt", "r+")
w.write("\nA;3")
print(w.readlines()[-1].strip())