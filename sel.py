#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import string
import random
import pandas as pd
from pprint import pprint


class Params():
    def __init__(self, count=10, filename='names.txt'):
        self.df_names = names(filename)
        self.user_list = self.users(count)

    def users(self, count):
        params = [self._user(self.df_names) for _ in range(count)]
        return params

    def _user(self, df):
        u = {'reg-password': randstr(12),
             'reg-website': randstr(8) + '.com',
             'id-nickname': df.Male.sample(1).values[0],
             'reg-firstname': df.Male.sample(1).values[0],
             'reg-lastname': df.Female.sample(1).values[0]
             }
        u['reg-email'] = u['reg-firstname'] + '@' + u['reg-website']
        u['reg-username'] = u['reg-firstname'] + randstr(3)

        return u


class DriverWrapper(webdriver.Firefox):
    def __init__(self, url='https://pentesttools.co.uk/'):
        super().__init__()
        self.url = url

    def register_users(self, users):
        for user in users:
            self.get(self.url)
            self.find_element(By.CSS_SELECTOR,
                              "ul > .page-item-61 > a").click()
            for key, value in user.items():
                self.find_element(By.ID, key).send_keys(value)

            self.find_element_by_id('submit-button').click()

    def check_el(self, element):
        elms = self.find_element(By.CSS_SELECTOR, element)
        pprint(elms)


def names(filename):
    df = pd.read_csv(filename, delimiter=' ', index_col=0)
    # df.to_pickle(filename)
    return df


def randstr(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


if __name__ == '__main__':
    url = 'https://pentesttools.co.uk/'
    p = Params()

    with DriverWrapper() as driver:
        driver.register_users(p.user_list)
