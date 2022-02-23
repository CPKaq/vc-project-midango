# Project Midango

## 简介

这是一个通过爬取 [萌娘百科](https://zh.moegirl.org.cn/Mainpage) 上的相关页面，读取 [周刊 VOCALOID 中文排行榜](https://space.bilibili.com/156489) （以及未来可能会延申到的 [其它类似榜单](https://zh.moegirl.org.cn/Template:%E6%A6%9C%E5%8D%95%E7%B1%BB%E8%A7%86%E9%A2%91) ）数据并保存为 json 文件的 Python 脚本。**爬取得到的所有数据可以在 [这里](https://github.com/CPKaq/vocaloid-china-biliran-data) 获取**。

本企划的名称来自 Bilibili 著名~~评论区~~ UP 主 [御坂美团](https://space.bilibili.com/4810592) 。

## 使用方法

运行 `moegirl_vc_weekly.py`。输入需要获取的起止期号（♪118 期后，左闭右开区间），即可获取每一期的排行榜数据并打包成 json 文件保存至 `/vc-weekly` 目录下（可能需要手动创建目录）。

极少量数据由于包含百科编辑者的勘误注释而需要手动处理，在命令行中会显示提示。

可以在 [vocaloid-china-biliran-data](https://github.com/CPKaq/vocaloid-china-biliran-data) 直接获取已修正的全部 json 数据。

## 工作原理

程序通过获取 MediaWiki 标记语言（即 “Wiki 源代码”，项目中简称为 Wikicode）以解析信息。

### `get_moegirl_vc_rank(week=None)`

这一函数返回 `week` 期周刊页面的源代码内容。这一过程是通过 `GET` 方式请求 `https://mzh.moegirl.org.cn/index.php?action=raw&title=周刊VOCALOID中文排行榜{期数}` 页面得到的。

附注：

* 据说 `mzh` 比 `zh` 站点更不容易触发 WAF；
* 访问一个 wiki 站点的页面时，本质上都是在向该站点的 `index.php` 提交一组 `action` 和 `title` 参数。其中 `action` 为 `view` 为查看页面，`edit` 为编辑页面，`history` 为查看编辑历史，`raw` 为直接返回源代码，`purge` 为强制刷新缓存（在建站修改 css 等时很有用）等。
* 感谢萌百编辑者长期坚持以 `周刊VOCALOID中文排行榜{期数}` 为固定标题格式创建页面。这使得批量获取页面信息极为方便。（若是在维基百科大概还需要考虑繁简互换之类的问题）

### `get_ranking_template(arg)` 

这个函数通过正则表达式获取页面中的所有 `{{VOCALOID_Chinese_Ranking/bricks}}` 模板。在周刊页面中使用这一模板得到格式化的周刊数据是固定格式。

正则表达式为：

``` regexp
\{\{VOCALOID_Chinese_Ranking/bricks\n[\S\s]*?\n\}\}
```

### `get_templ_param(para, arg)`

这个函数通过正则表达式匹配 wiki 模板内容中的参数—键值对。

wiki 模板的格式通常为：

``` regexp
{{template name
| param1 = value1
| param2 = value2
| ...
| paramN = valueN
}}
```

因此对于参数，`{para}` 使用正则表达式：

``` regexp
(?<=\|{para} =)[\S ]*(?=\n)
```

### `try_int(arg: str)` 及 `try_float(arg: str)`

尝试将需要转换为数字的参数字符串转换为参数。部分内容无法转换时，不转换字符串，并在终端命令行中输出错误信息。如 ♪129 期 第 7 名《神经病之歌》的相关模板中：

``` regexp
|收藏 = 43<ref>此处数据为周刊组笔误，实为247</ref>
```

此时不会转换，并在目标 json 文件中保留字符串形式，待手动修正：

```json
    "favorite": "43<ref>此处数据为周刊组笔误，实为247</ref>"
```

### `try_av(arg: str) -> int`

尝试将视频编号转换为数字形式的 av 号。

* 当字符串为纯数字时直接转换；
* 当字符串以 `av` 开头时，去掉前两个字母转换剩下的数字；
* 当字符串以 `bv` 开头时，调用函数 `bv2av(arg: str)` 转换 BV 号为 av 号。
  * ~~奇怪，为什么编辑组用的是 `bv` 而非 Bilibili 默认的 `BV` 呢~~

### `bv2av(arg: str) -> int`

魔改自知乎用户 [mcfx](https://www.zhihu.com/question/381784377/answer/1099438784) 的 BV 转 av 算法。

由于需要大规模使用，因此把初始化字典的循环给展开了，然后也省略了 magic number 的声明 ~~反正原本的变量名就看不懂~~ 。结果就是代码看起来更魔法了。

原作者将代码以 WTFPL 开源。

``` python
def bv2av(arg: str) -> int:
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
```

### 其他

`output_json(week=None)` 函数用于输入期数并完成从获取信息到保存 json 文件的全部工作。其中有对 wiki 模板的过滤，即忽略掉含有以下内容的模板信息：

* `本周 = OP`，因为每期 OP 可以从上一期排名得知；
* `本周 = ED`，没有当周统计信息，可能以后会专门统计；
* `H I S T O R Y`，历史回顾可以查询往期排名得知；
* `本周 = [0-9]+.5`，这是编辑组对部分歌曲的架空 “虚拟排名”，并非真实排名。

`wikicode_to_dict(arg)` 函数将一个 wiki 模板的完整代码转换为一个 `dict` 字典对象并返回。其中：

* Super Hit 曲目的排名记作 `0`，同时无修正 A 和修正 B 记录；
* 发布时间中 `/` 均替换为 `-`，以符合 `yyyy-MM-dd HH:mm` 标准（♪481 期起出现了 `yyyy/MM/dd HH:mm` 的记录方法）。
  * 这一条和上面的 av / BV 号记录方法是萌百周刊条目中仅有的两条前后未能统一之处。