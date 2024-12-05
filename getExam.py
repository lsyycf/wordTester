import json
import os
import random


def get_random_word(word_list, used_list, known_list):
    out_list = used_list + known_list
    out_list = sorted(list(set(out_list)))
    list_temp = [word for word in word_list if word["index"] not in out_list]
    random_word = random.choice(list_temp)
    return random_word


def merge_json(file_dir, day, index_list, all_list):
    path = os.path.join(file_dir, f'day_{day}.json')
    list_merge = index_list.copy()
    if os.path.exists(path):
        with open(path, 'r', encoding="utf-8") as f:
            json_str = f.read()
            if json_str:
                dict_from_json = json.loads(json_str)
                for word in dict_from_json:
                    list_merge.append(word["index"])
            list_merge = sorted(list(set(list_merge)))
    word_merge = [word for word in all_list if word["index"] in list_merge]
    word_merge.sort(key=lambda x: x['index'])
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(word_merge, ensure_ascii=False, indent=2))
