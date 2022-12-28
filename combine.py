import json

out_list = list()

sub_nodes = ["68","67","69","66","65"]

with open("map_doublev2.json","r") as target:
    for edge in json.load(target):
        if any([x in edge[0] for x in sub_nodes]):
            out_list.append(edge)
            continue
        elif any([x in edge[1] for x in sub_nodes]):
            out_list.append(edge)
            continue

with open("map_small.json","w+") as target:
    json.dump(out_list,target)