#!/usr/bin/env python
import sys
import json
import yaml
import os
import re
import time
import requests
import numpy as np
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from datetime import date, datetime


class ZaimDownLoader(object):

    def __init__(self, id_, pass_):
        self.url = 'https://auth.zaim.net'
        self.id_ = id_
        self.pass_ = pass_
        self.driver = webdriver.PhantomJS()

    def output_zaim_datafile(self, output_file):

        self.__login()
        time.sleep(5)

        df_rev = pd.DataFrame()
        end_date = date.today()
        start_date = date(2016, 1, 1)

        for single_date in self.__monthrange(start_date, end_date):
            YYYYmm = single_date.strftime("%Y%m")
            print("Downloading {0} money data.".format(YYYYmm))
            df = pd.DataFrame(self.__fetch_a_month_money_data(YYYYmm))
            df.iloc[:, 2:3] = YYYYmm[0:4] + '-' + df.iloc[:, 2:3]
            df_rev = pd.concat([df_rev, df])

        df_rev.columns = ["edit", "aggregate", "date", "category", "genre",
                          "amount", "from_account", "to_account", "place",
                          "name", "comment"]

        df_rev['genre'] = df_rev['genre'].apply(lambda x:
                                                str(x).split('\n')[1])

        # remove not_aggregated amount
        df_rev = df_rev[df_rev['aggregate'] == 'add_circle_outline']

        # remove edit & aggregate columns
        df_rev = df_rev.iloc[:, 2:]

        SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
        output_path = SCRIPT_PATH + "/" + output_file

        with open(output_path, encoding='utf-8', mode='w') as a_file:
            a_file.write(
                self.__trim_json_4_elasticsearch(
                    df_rev.to_json(orient='records', force_ascii=False)
                )
            )

    def __fetch_a_month_money_data(self, YYYYmm):

        self.driver.get("https://zaim.net/money?month={0}".format(YYYYmm))

        page = self.driver.page_source.encode('utf-8')
        html = BeautifulSoup(page, "lxml")
        table = html.find('table', attrs={'class': 'list'})

        if table:
            data = self.__html_table_2_list(table)
        else:
            data = []

        return data

    def __login(self):
        self.driver.get(self.url)
        self.driver.find_element_by_name(
            'data[User][email]').send_keys(self.id_)
        self.driver.find_element_by_name(
            'data[User][password]').send_keys(self.pass_)
        self.driver.find_element_by_xpath("//*[@id='UserLoginForm']/div[4]/input").click()

    def __get_json(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html, "lxml")
        json_list = soup.find("pre").contents
        json_data = ''.join(json_list)
        return json_data

    def __trim_json_4_elasticsearch(self, json_data):
        json_data_rev = re.sub('(\]|\[)', '', json_data)
        json_data_rev = json_data_rev.replace('},', '}\n')
        json_data_rev = re.sub('^', '{ "index" : {} }\n',
                               json_data_rev, flags=re.MULTILINE)
        return json_data_rev

    def __monthrange(self, start_date, end_date):
        result = []
        while start_date <= end_date:
            result.append(start_date)
            start_date += relativedelta(months=1)
        return result[::-1]

    def __jpdate_2_date(self, jpdate):
        a = str(jpdate).split('月')
        date_str = a[0] + '-' + a[1].split('日')[0]
        return date_str

    def __html_table_2_list(self, table):
        data = []
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows[1:-3]:  # skip the empty header row and summary row
            cols_rev = []
            cols = row.find_all('td')
            for ele in cols:
                match1 = re.match('(\d{1,2})[/\.月](\d{1,2})日?', ele.text.strip())
                match2 = re.match('(¥\d{1,3})(,\d{3})*$', ele.text.strip())
                if ele.find('span', attrs={'data-toggle': 'tooltip'}):
                    if ele.find('span', attrs={'class': 'material-icons icon-sm'}):
                        cols_rev.append(ele.find('span').get('data-title')) # category
                        cols_rev.append(ele.text.strip()) # genre
                    else:
                        # place and comment
                        cols_rev.append(ele.find('span').get('data-original-title'))
                elif ele.find('img', attrs={'class':'account-sm'}):
                    cols_rev.append(ele.find('img').get('data-title')) # account
                elif match1:
                    # convert japanese date to universal date expression.
                    univ_date = match1.groups()[0] + '-' + match1.groups()[1]
                    cols_rev.append(univ_date) # date
                elif match2:
                    # remove ¥ and comma from amount
                    amount = match2.group().replace('¥', '')
                    amount = amount.replace(',', '')
                    cols_rev.append(amount)  # amount
                else:
                    cols_rev.append(ele.text.strip())  # else
            #cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols_rev])
        return data

def main():
    SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
    config_file = SCRIPT_PATH + "/" + "config.yml"
    conf = yaml.load(open(config_file).read())

    ID = conf['ID']
    PASS = conf['PASS']

    zdl = ZaimDownLoader(ID, PASS)
    zdl.output_zaim_datafile("data.json")

if __name__ == '__main__':
    main()
