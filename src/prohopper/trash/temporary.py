# def remap(values: List, source: List = List(0, 1), target: List = List(0, 1)):
#     new_lists = list_longest(source, target)
#     source = new_lists[0];
#     target = new_lists[1]
#     print(source, target)
#     source_dis = source[1] - source[0]
#     target_dis = target[1] - target[0]
#     result = [(i - source[0]) / source_dis * target_dis + target[0] for i in values]
#     return result
