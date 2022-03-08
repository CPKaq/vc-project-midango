import re
import json
import time
import httpx


def main():
    start, end = input("获取开始结束区间(118~)").split()
    for w in range(int(start), int(end)):
        r = output_json(w)
        if r == -1:
            print("连接被阻断。")
            # break
        time.sleep(2)
        # 客户加钱优化时删除
        # ↑其实是防止爬取频率过高导致萌百阻断连接
    # input()


def output_json(week=None):
    wiki_code = None
    while wiki_code is None:
        wiki_code = get_moegirl_vc_rank(week=week)
    templates = get_ranking_template(wiki_code)
    if not templates:
        return -1

    file_name = "./vc-weekly/{}.json".format(week)
    with open(file_name, mode='w', encoding='utf-8') as f:
        template_rank_list = []
        for text in templates:
            if (re.search(r'本周 = OP', text) or re.search(r'本周 = ED', text)
                    or re.search(r'H I S T O R Y', text) or re.search(r'本周 = [0-9]+.5', text)):
                continue
            template_rank_list.append(wikicode_to_dict(text))

        j = json.dumps(template_rank_list, ensure_ascii=False, indent=4)
        # print(j)
        f.write(j)
    print("已获取第{}期".format(week))
    return 0


def get_moegirl_vc_rank(week=None):
    url = 'https://mzh.moegirl.org.cn/index.php'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.128 Safari/537.36"}
    params = {'title': '周刊VOCALOID中文排行榜' + str(week), 'action': 'raw'}
    try:
        req = httpx.get(url, headers=headers, params=params, timeout=None)
        s = req.text
        return s
    except Exception as e:
        print(e)
        return None


def get_ranking_template(arg):
    pattern = r"\{\{VOCALOID_Chinese_Ranking/bricks\n[\S\s]*?\n\}\}"
    return re.findall(pattern, arg)


def get_templ_param(para, arg):
    pattern = r"(?<=\|{} =)[\S ]*(?=\n)".format(para)
    s = re.search(pattern, arg)
    if s:
        # print("found "+para)
        return s.group(0).strip()
    else:
        # print("not found "+para)
        return ""


def wikicode_to_dict(arg):
    seq = ('id', 'title', 'isCover', 'date', 'rank', 'point', 'view', 'favorite', 'reply', 'danmaku', 'corrA', 'corrB')
    d = dict.fromkeys(seq)

    d['id'] = try_av(get_templ_param("id", arg))
    d['title'] = get_templ_param("曲名", arg)
    d['rank'] = get_templ_param("本周", arg)

    d['isCover'] = (get_templ_param("翻唱", arg) != "")

    d['date'] = get_templ_param("时间", arg).replace("/", "-")

    d['point'] = try_int(get_templ_param("得点", arg))
    d['view'] = try_int(get_templ_param("播放", arg))
    d['favorite'] = try_int(get_templ_param("收藏", arg))
    d['reply'] = try_int(get_templ_param("评论", arg))
    d['danmaku'] = try_int(get_templ_param("弹幕", arg))

    rank_str = get_templ_param("本周", arg)
    if rank_str == "SH":
        d['rank'] = 0
    else:
        d['rank'] = try_int(rank_str)
        d['corrA'] = try_float(get_templ_param("弹幕权重", arg))
        d['corrB'] = try_float(get_templ_param("收藏权重", arg))
    # print(d)
    return d


def try_int(arg: str):
    try:
        r = int(arg.replace(',', ''))
    except ValueError:
        print("无法转换int: " + arg)
        return arg
    else:
        return r


def try_float(arg: str):
    try:
        r = float(arg)
    except ValueError:
        print("无法转换float: " + arg)
        return arg
    else:
        return r


def try_av(arg: str) -> int:
    r = None
    try:
        r = int(arg)
    except ValueError:
        if arg[0] == 'a':
            r = int(arg[2:])
        elif arg[0] == 'b' or arg[0] == 'B':
            r = bv2av(arg)
    finally:
        return r


def bv2av(arg: str) -> int:
    # 修改自知乎: mcfx
    # https://www.zhihu.com/question/381784377/answer/1099438784
    tr = {'f': 0, 'Z': 1, 'o': 2, 'd': 3, 'R': 4, '9': 5, 'X': 6, 'Q': 7, 'D': 8, 'S': 9, 'U': 10, 'm': 11,
          '2': 12, '1': 13, 'y': 14, 'C': 15, 'k': 16, 'r': 17, '6': 18, 'z': 19, 'B': 20, 'q': 21, 'i': 22,
          'v': 23, 'e': 24, 'Y': 25, 'a': 26, 'h': 27, '8': 28, 'b': 29, 't': 30, '4': 31, 'x': 32, 's': 33,
          'W': 34, 'p': 35, 'H': 36, 'n': 37, 'J': 38, 'E': 39, '7': 40, 'j': 41, 'L': 42, '5': 43, 'V': 44,
          'G': 45, '3': 46, 'g': 47, 'u': 48, 'M': 49, 'T': 50, 'K': 51, 'N': 52, 'P': 53, 'A': 54, 'w': 55,
          'c': 56, 'F': 57}
    s = (11, 10, 3, 8, 4, 6)
    r = 0
    for i in range(6):
        r += tr[arg[s[i]]] * 58 ** i
    return (r - 8728348608) ^ 177451812


if __name__ == '__main__':
    main()
