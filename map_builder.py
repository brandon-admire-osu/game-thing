import json
from ClassesAndObjects import Edge

if __name__ == "__main__":
    out_set = list()
    while True:
        near = input("Near: ")
        if near == "d":
            print(out_set)
            continue


        far = input("Far: ")
        if near == '' and far == '':
            break

        if near == '' or far == '':
            continue

        special = input("Type: ")
        if special == '':
            special = 0

        cur = Edge(near,far,special)
        if cur not in out_set: #Check for duplicates
            out_set.append(cur)
    

    with open("map2.json","w+") as target:
        out_list = list()
        for edge in out_set:
            out_list.append(f"({edge.A},{edge.B})")
        json.dump(out_list,target)