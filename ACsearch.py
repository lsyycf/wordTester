import json
import os
import re
import shutil
from collections import deque
from readBook import read_pdf


def ignore(c):
    return c == ' ' or c == '\n' or c == '\t' or c == '\r' or c == '\f' or c == '\v'


class TrieNode:
    def __init__(self):
        self.children = {}
        self.fail = None
        self.output = []


class AC:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, pattern, index):
        node = self.root
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.output.append(index)

    def build(self):
        queue = deque()
        for char, node in self.root.children.items():
            node.fail = self.root
            queue.append(node)
        while queue:
            current_node = queue.popleft()
            for char, child_node in current_node.children.items():
                fail_node = current_node.fail
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail
                if fail_node is None:
                    child_node.fail = self.root
                else:
                    child_node.fail = fail_node.children[char]
                    child_node.output.extend(child_node.fail.output)
                queue.append(child_node)

    def search(self, text, patterns):
        node = self.root
        matches = set()
        count = 0
        for i in range(len(text)):
            if ignore(text[i]):
                i += 1
                count += 1
                continue
            while node is not None and text[i] not in node.children:
                node = node.fail
                count = 0
            if node is None:
                node = self.root
                count = 0
                continue
            node = node.children[text[i]]
            if node.output:
                for pattern_index in node.output:
                    matches.add(i - len(patterns[pattern_index]) + 1 - count)
                count = 0
        return sorted(list(matches))


def split_by_matches(text, matches):
    segments = []
    start_idx = 0
    for match in matches:
        result = re.sub(r"^[\s\v\f\r\n\t]+|[\s\v\f\r\n\t]+$", "", text[start_idx:match])
        if result != '':
            segments.append(result)
        start_idx = match
    result = re.sub(r"^[\s\v\f\r\n\t]+|[\s\v\f\r\n\t]+$", "", text[start_idx:])
    segments.append(result)
    return segments


def split_text(text, patterns):
    patterns = [re.sub(r"[\s\v\f\r\n\t]+", '', pattern).strip() for pattern in patterns]
    ac = AC()
    for i, pattern in enumerate(patterns):
        ac.insert(pattern, i)
    ac.build()
    matches = ac.search(text, patterns)
    splits = split_by_matches(text, matches)
    return splits


def remove_before(content):
    pattern = 'N0.WordMeaningN0.WordMeaning'
    match = re.search(pattern, content)
    if match:
        content = content[match.end():]
    list_temp = ''
    for i in range(2, 41):
        target_str = str(i)
        match = re.search(rf"(?={target_str})", content)
        if not match:
            break
        else:
            list_temp += content[:match.start()] + '\n'
            content = content[match.end():]
    return list_temp + content


def parse_word_desc(word_desc):
    match = re.match(r"(\d+)(.*?)\[([^\]]+)\](.*)", word_desc)
    if match:
        index = match.group(1)
        word = match.group(2).strip()
        phonetic = f"[{match.group(3)}]"
        meanings = []
        parts = re.findall(r'([a-zA-Z. ]+)\. (.*?)(?=\s*[a-zA-Z. ]+\. |$)', match.group(4), re.DOTALL)
        for pos, meaning in parts:
            meanings.append(f'{pos.strip()}' + '.' + f'{meaning.strip()}')

        result = {
            "index": int(index),
            "word": word,
            "phonetic": phonetic,
            "meanings": " ".join(meanings),
            "wrong": 0
        }
        return result
    return None


def formatter(text):
    patterns = ['炭炭背单词']
    split = split_text(text, patterns)
    file_dir = 'list'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    for i, part in enumerate(split, 1):
        part = remove_before(part)
        words = []
        for line in part.split('\n'):
            if line.strip() != '':
                words.append(parse_word_desc(line))
        file_path = os.path.join(file_dir, f'day_{i}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(words, ensure_ascii=False, indent=2))


def book(path):
    content = read_pdf(path)
    wrong_dir = 'wrong'
    if os.path.exists(wrong_dir):
        shutil.rmtree(wrong_dir)
    known_dir = 'known'
    if os.path.exists(known_dir):
        shutil.rmtree(known_dir)
    list_dir = 'list'
    if os.path.exists(list_dir):
        shutil.rmtree(list_dir)
    if os.path.exists("schedule.json"):
        os.remove("schedule.json")
    if not content:
        return ["警告", "未找到词书内容"]
    formatter(content)
    return ["提示", f'词书导入成功']
