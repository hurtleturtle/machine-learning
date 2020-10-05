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
import os
import json


class Params():
    def __init__(self, user_count=10, comment_count=10):
        self.df_names = self._get_names('names.txt')
        self.words = self._get_words('/usr/share/dict/words')
        self.users = self._build_list(self._user, user_count)
        self.comments = self._build_list(self._comment, comment_count)
        self.save_users()

    def _build_list(self, param, count):
        params = [param() for _ in range(count)]
        return params

    def _get_name(self, name_type='first_name'):
        return self.df_names[name_type].sample(1).values[0]

    def _get_names(self, filename):
        df = pd.read_csv(filename, delimiter=' ')
        return df

    def _get_words(self, filename):
        with open(filename) as f:
            return f.read().splitlines()

    def _user(self):
        u = {'reg-password': randstr(12),
             'reg-website': randstr(8) + '.com',
             'id-nickname': self._get_name(),
             'reg-firstname': self._get_name(),
             'reg-lastname': self._get_name(name_type='last_name')
             }
        u['reg-email'] = u['reg-firstname'] + '@' + u['reg-website']
        u['reg-username'] = u['reg-firstname'] + randstr(3, string.digits)

        return u

    def save_users(self, users=None, filename='users.json'):
        if not users:
            users = [{'username': u['reg-username'],
                      'password': u['reg-password']} for u in self.users]
        old_users = self.load_users(filename=filename)
        users.extend(old_users)

        with open(filename, 'w') as f:
            json.dump(users, f)

    def load_users(self, filename='users.json'):
        if os.path.isfile(filename):
            with open(filename) as f:
                users = json.load(f)
        else:
            users = []

        return users

    def _comment(self):
        comment = {'comment': ' '.join(random.choices(self.words,
                                                      k=random.randint(10,
                                                                       100))),
                   'author': (self._get_name() + ' ' +
                              self._get_name('last_name')),
                   'url': randstr(10) + '.com'
                   }
        comment['email'] = comment['author'].replace(' ', '@') + comment['url']

        return comment


class DriverWrapper(webdriver.Firefox):
    def __init__(self, url='https://pentesttools.co.uk/'):
        super().__init__()
        self.url = url

    def register_users(self, users):
        for user in users:
            self.get(self.url)
            self.find_element(By.CSS_SELECTOR,
                              'ul > .page-item-61 > a').click()
            for key, value in user.items():
                self.find_element(By.ID, key).send_keys(value)

            self.find_element_by_id('submit-button').click()

    def post_comments(self, comments):
        for comment in comments:
            self.get(self.url)
            self.find_element(By.CSS_SELECTOR,
                              'ul > .page-item-55 > a').click()
            for key, value in comment.items():
                self.find_element(By.ID, key).send_keys(value)

            self.find_element_by_id('submit').click()

    def test_logins(self, users):
        for user in users:
            self.get(self.url)
            self.find_element(By.CSS_SELECTOR, ".home").click()
            self.find_element(By.LINK_TEXT, "Log In").click()
            self.find_element(By.ID, "login-name").send_keys(user['username'])
            self.find_element(By.ID, "login-pass").send_keys(user['passwd'])
            self.find_element(By.NAME, "login_submit").click()

    def check_el(self, element):
        elms = self.find_element(By.CSS_SELECTOR, element)
        pprint(elms)


def randstr(length, chars=string.ascii_letters):
    return ''.join(random.choices(chars, k=length))


if __name__ == '__main__':
    url = 'https://pentesttools.co.uk/'
    p = Params(user_count=10, comment_count=10)

    with DriverWrapper() as driver:
        driver.register_users(p.users)
        driver.post_comments(p.comments)
        driver.test_logins(p.load_users())
