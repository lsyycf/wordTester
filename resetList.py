import json
import os


def load_dictionary(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def get_all_list(day):
    file_dir = 'known'
    file_path = f"list/day_{day}.json"
    all_list = load_dictionary(file_path)
    path = os.path.join(file_dir, f'day_{day}.json')
    if os.path.exists(path):
        with open(path, 'r', encoding="utf-8") as f:
            json_str = f.read()
            if json_str:
                dict_from_json = json.loads(json_str)
            all_list += dict_from_json
    return all_list


def reset(day):
    file_path = f"list/day_{day}.json"
    if not os.path.exists(file_path):
        return ["警告", "该目录不存在"]
    if os.path.exists('known'):
        all_list = get_all_list(day)
    else:
        all_list = load_dictionary(file_path)
    for word in all_list:
        word['wrong'] = 0
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(all_list, ensure_ascii=False, indent=2))
    if os.path.exists(f"known/day_{day}.json"):
        os.remove(f"known/day_{day}.json")
    if os.path.exists(f"wrong/day_{day}.json"):
        os.remove(f"wrong/day_{day}.json")
    if os.path.exists('schedule.json'):
        with open("schedule.json", "r", encoding="utf-8") as f:
            schedule = json.load(f)
        for date in schedule:
            for task in date["task"]:
                if task["num"] == day:
                    task["finish"] = '0'
        with open("schedule.json", "w", encoding="utf-8") as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)
    return ["提示", f"list_{day}重置成功"]
