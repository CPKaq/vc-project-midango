# Project Midango

## 简介

这是一个通过爬取 [萌娘百科](https://zh.moegirl.org.cn/Mainpage) 上的相关页面，读取 [周刊 VOCALOID 中文排行榜](https://space.bilibili.com/156489) （以及未来可能会延申到的 [其它类似榜单](https://zh.moegirl.org.cn/Template:%E6%A6%9C%E5%8D%95%E7%B1%BB%E8%A7%86%E9%A2%91) ）数据并保存为 json 文件的 Python 脚本。**爬取得到的所有数据可以在 [这里](https://github.com/CPKaq/vocaloid-china-biliran-data) 获取**。

本企划的名称来自 Bilibili 著名~~评论区~~ UP 主 [御坂美团](https://space.bilibili.com/4810592) 。

## 使用方法

运行 `moegirl_vc_weekly.py`。输入需要获取的起止期号（♪118 期后，左闭右开区间），即可获取每一期的排行榜数据并打包成 json 文件保存至 `/vc-weekly` 目录下（可能需要手动创建目录）。

极少量数据由于包含百科编辑者的勘误注释而需要手动处理，在命令行中会显示提示。

可以在 [vocaloid-china-biliran-data](https://github.com/CPKaq/vocaloid-china-biliran-data) 直接获取已修正的全部 json 数据。