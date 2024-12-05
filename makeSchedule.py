import json
import os
import shutil


def generate(numbers, review):
    wrong_dir = 'wrong'
    if os.path.exists(wrong_dir):
        shutil.rmtree(wrong_dir)
    known_dir = 'known'
    if os.path.exists(known_dir):
        shutil.rmtree(known_dir)
    numbers.insert(0, 0)
    review.insert(0, "list")
    file_num = 0
    if not os.path.exists("list"):
        return ["警告", "请先导入词书"]
    for file in os.listdir("list"):
        if file.endswith(".json"):
            file_num += 1
    if file_num == 0:
        return ["警告", "请先导入词书"]
    dicts = []
    for day in range(1, file_num + numbers[-1] + 1):
        lists = []
        test_data = 1
        for _ in range(1, len(numbers) + 1):
            if 0 < day - numbers[_ - 1] <= file_num:
                test = {
                    "test": test_data,
                    "type": review[_ - 1],
                    "num": day - numbers[_ - 1],
                    "finish": "0"
                }
                test_data += 1
                lists.append(test.items())
        dicts.append({
            "day": day,
            "task": [dict(x) for x in lists]
        })
    with open("schedule.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(dicts, ensure_ascii=False, indent=2))
    return ["提示", "学习计划制定成功"]
