#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import traceback
import time

import xlwt
import chardet

from browser import BaiduBrowser
from utils.log import logger
from config import IniConfig
from city import final_city_dict

data_dict = dict()

ini_config = IniConfig()
index_type_dict = {
    'all': u'整体趋势', 'pc': u'PC趋势', 'wise': u'移动趋势'
}


def save_cookie_to_file(cookie_json):
    with open(ini_config.cookie_file_path, 'w') as f:
        f.write(cookie_json)


def load_cookie_from_file():
    cookie_json = ''
    if os.path.exists(ini_config.cookie_file_path):
        with open(ini_config.cookie_file_path, 'r') as f:
            cookie_json = f.read()
    return cookie_json


def main():
    logger.info(u'请确保你填写的账号密码能够成功登陆百度')
    # 创建data目录
    result_folder = ini_config.out_file_path
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    # 加载曾经保存的cookie文件,尽量避免重复登录
    cookie_json = load_cookie_from_file()
    baidu_browser = BaiduBrowser(cookie_json=cookie_json)
    # 将登陆成功后的cookie_json保存到文件
    save_cookie_to_file(baidu_browser.get_cookie_json())
    logger.info(u'登陆成功')

    fp = open(ini_config.keywords_task_file_path, 'rb')
    task_list = fp.readlines()
    fp.close()

    root = os.path.dirname(os.path.realpath(__file__))
    result_folder = os.path.join(root, ini_config.out_file_path)
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    for index, keyword in enumerate(task_list):
        try:
            keyword = keyword.strip()
            if not keyword:
                continue
            parse_one_keyword(keyword, result_folder, baidu_browser)
        except:
            print traceback.format_exc()

    file_name = u'result-' \
                + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time())) \
                + u'.xls'
    file_name = file_name.encode(
        ini_config.file_name_encoding, 'ignore'
    )
    file_path = os.path.join(result_folder, file_name)
    write_excel(file_path)


def parse_one_keyword(keyword, result_folder, baidu_browser):
    area_list = ini_config.area_list.split(',')
    area_list = [_.strip() for _ in area_list]
    type_list = ini_config.index_type_list.split(',')
    type_list = [_.strip() for _ in type_list]

    detect_result = chardet.detect(keyword)
    encoding = detect_result['encoding'] if detect_result else 'gbk'
    keyword_unicode = keyword.decode(encoding, 'ignore')
    logger.info('%s start' % keyword_unicode)
    for area in area_list:
        for type_name in type_list:
            baidu_index_dict = baidu_browser.get_baidu_index(
                keyword_unicode, type_name, area
            )
            date_list = sorted(baidu_index_dict.keys())

            type_name_zh = index_type_dict.get(type_name)
            file_name = u'%s_%s_%s.xls' % (
                keyword_unicode,
                final_city_dict[area],
                type_name_zh
            )

            data_list = []
            for date in date_list:
                value = baidu_index_dict[date]
                data_list.append(
                    (keyword_unicode, date, type_name_zh, value)
                )

            data_dict[keyword_unicode] = data_list
            # write_excel(file_path, data_list, keyword_unicode, index)


def write_excel(excel_file):
    global data_dict
    wb = xlwt.Workbook()
    ws = wb.add_sheet(u'工作表1')
    ws.write(0, 0, u'日期')
    index = 1
    for key, value in data_dict.items():
        ws.write(0, index, key)
        row = 1
        for result in value:
            if index == 1:
                ws.write(row, 0, result[1])
            ws.write(row, index, result[3])
            row += 1
        index += 1
    wb.save(excel_file)


if __name__ == '__main__':
    main()