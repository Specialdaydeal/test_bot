from selenium.webdriver import Firefox, FirefoxProfile, Keys
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from os import remove, path
import sqlite3 as sl
import pyautogui as gui
from time import sleep, perf_counter
from random import random, randrange
import pickle
from string import ascii_uppercase as letters


class Browser:
    config = {"lang": "en",
              "is_mobile": True,
              "user_agent": "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Mobile Safari/537.36",
              "device": {"width": 320, "height": 640}
              }
    timeout = 20
    profile = {}
    driver = {}
    closed = True
    start_time = 0
    COOKIE_FILE_NAME = "cookies.pkl"
    db = None

    def __init__(self):
        self.start_time = datetime.now()
        self.db = sl.connect('my.db')

        gui.FAILSAFE = True
        self.check_log_file()

    def load_profile(self):
        print("1. profile load")
        try:
            self.profile = FirefoxProfile()
            self.profile.set_preference("intl.accept_languages", self.config["lang"])
            self.profile.set_preference("general.useragent.override", self.config["user_agent"])
            self.profile.set_preference("browser.privatebrowsing.autostart", True)
            self.profile.set_preference("dom.webdriver.enabled", False)
            self.profile.set_preference('useAutomationExtension', False)
            self.profile.update_preferences()
        except:
            self.close("1. except")

    def start_driver(self):
        print("2. driver start")
        self.closed = False
        try:
            self.driver = Firefox(executable_path=r'./geckodriver', firefox_profile=self.profile)

            if self.config["is_mobile"]:
                self.driver.set_window_size(self.config["device"]["width"], self.config["device"]["height"])
        except:
            self.close("2. except")

    def load_browser_config(self):
        print("3. browser config")
        if not self.closed:
            try:
                self.config["size"] = self.driver.get_window_size()

                pos = self.driver.get_window_position()
                self.config["offset_x"] = pos["x"] + 5
                self.config["offset_y"] = pos["y"] + 90
            except:
                self.close("3. except")

    def linkedin_login(self):
        print("start login")
        sleep(2)
        self.driver.find_element(By.ID, "username").send_keys("master_miko@bk.ru")
        self.driver.find_element(By.ID, "password").send_keys("master666")
        sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".login__form_action_container button.from__button--floating").click()

    def save_cookie(self):
        cookies = self.driver.get_cookies()
        print(cookies)
        x = {}
        for cookie in cookies:
            if cookie['name'] == 'li_at':
                cookie['domain'] = '.linkedin.com'
                x = {
                    'name': 'li_at',
                    'value': cookie['value'],
                    'domain': '.linkedin.com'
                }
                break
        pickle.dump(x, open(self.COOKIE_FILE_NAME, "wb"))
        print('cookies saved')

    def load_cookie(self):
        if path.exists(self.COOKIE_FILE_NAME):
            cookies = pickle.load(open(self.COOKIE_FILE_NAME, "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            print('cookies loaded')

    def search(self):
        print("4. search")
        if not self.closed:
            try:
                self.driver.get("https://google.com/")
                search_form = self.wait_show_element("input[name=q]")
                if search_form is None:
                    self.close("search input none")
                else:
                    if self.config["is_mobile"]:
                        self.close_dialog_mobile()
                    else:
                        self.close_dialog()

                    self.click(search_form)
                    sleep(randrange(3))

                    self.type(self.config["keyword"])
                    gui.press("enter")

                    self.get_ads_el()
            except UnexpectedAlertPresentException:
                self.close("8. UnexpectedAlertPresentException")
            except:
                self.close("8. except")

    def close_dialog_mobile(self):
        print("8.1. close dialog mobile")
        if not self.closed and not self.config["login"]:
            button = self.wait_show_element("#cnskx")
            if button:
                self.click(button)
                sleep(1)
                gui.click()
                sleep(randrange(3))

    def close_dialog(self):
        print("8.1. close dialog web")
        if not self.closed and not self.config["login"]:
            agree_button = self.wait_show_element("#L2AGLb")
            if agree_button:
                self.move_to_el(agree_button)
                sleep(randrange(3))
                gui.click()
                sleep(randrange(3))

    def add_job_title(self, title):
        try:
            cur = self.db.cursor()
            cur.execute('INSERT INTO jobs(title) VALUES(?)', (title,))
            self.db.commit()
        except:
            pass

    def close(self, reason=None):
        if not self.closed:
            self.closed = True
            self.db.close()
            sleep(1)
            try:
                self.driver.quit()
            except:
                print("closed error")
                sleep(3)
            print("#. Closed: {0}".format(reason))
        print("time: {0}".format((datetime.now() - self.start_time).total_seconds()))
        print("* * * * *")

    @staticmethod
    def type(query):
        for q in query:
            gui.press(q)

    def move_to_el(self, e):
        if not self.closed:
            try:
                current_position = self.driver.execute_script("return window.scrollY")
                if current_position + self.config["size"]["height"] > e.location["y"] + e.size["height"]:
                    gui.moveTo(
                        e.location["x"] + self.config["offset_x"] + randrange(3, int(e.size["width"]) - 3),
                        e.location["y"] - current_position + self.config["offset_y"] + randrange(3, int(
                            e.size["height"]) - 3),
                        random())
                else:
                    self.scroll_element(e)
            except UnexpectedAlertPresentException:
                self.close("UnexpectedAlertPresentException")
            except:
                self.close("except")

    def scroll_element(self, e):
        if not self.closed:
            try:
                start_time = perf_counter()
                current_position = self.driver.execute_script("return window.scrollY")
                target = e.location["y"] - self.config["size"]["height"] + e.size["height"]
                while current_position <= target:
                    gui.scroll(-1 * int(self.config["size"]["height"] / 20))
                    current_position = self.driver.execute_script("return window.scrollY")
                    sleep(randrange(3))
                    if perf_counter() - start_time > self.timeout:
                        self.close("scroll timeout")
                        break
                if not self.closed:
                    self.move_to_el(e)
            except:
                print("not found")

    def click(self, element):
        try:
            self.move_to_el(element)
            gui.click()
            return True
        except:
            return False

    def wait_show_element(self, selector):
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            return element
        except:
            return None

    def join_domains(self, items):
        domains = ""
        for item in items:
            if item.domain == "Google Play" or item.domain == "App Store":
                domains += item.ad_text + ","
            else:
                domains += item.domain + ","
        return domains

    def wait_load_url(self, url):
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            url = wait.until(EC.url_contains(url))
            return url
        except:
            return None

    def search_job(self):
        search_input = self.get_element("#postitle")
        if search_input.is_displayed():
            search_input.click()

        next_search = True
        search_key = letters[0]
        while next_search:
            gui.typewrite(search_key[-1])

            items_len = self.add_items()

            if items_len == 20:
                search_key += letters[0]
            else:
                letter_index = 1 + letters.find(search_key[-1])
                if letter_index == len(letters):
                    search_key = search_key[:-1]
                    gui.hotkey("backspace")

                    letter_index = 1 + letters.find(search_key[-1])

                new_key = letters[letter_index]
                search_key = search_key[:-1]
                gui.hotkey("backspace")
                search_key += new_key

    def add_items(self):
        sleep(2)
        element = self.driver.find_element(By.ID, "edit-position-typeahead-results")
        items = element.find_elements(By.CLASS_NAME, "simple-item")
        items_len = len(items)
        if items_len > 0:
            for item in items:
                self.add_job_title(item.text)

        return items_len

    def wait_hide_element(self, selector):
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            element = wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, selector)))
            return element
        except:
            return None

    def get_element_from(self, object, selector):
        try:
            return object.find_element_by_css_selector(selector)
        except NoSuchElementException:
            return None

    def get_elements_from(self, object, selector):
        try:
            return object.find_elements_by_css_selector(selector)
        except NoSuchElementException:
            return None

    def get_element(self, selector):
        return self.get_element_from(self.driver, selector)

    def get_elements(self, selector):
        return self.get_elements_from(self.driver, selector)

    def get_parent_node(self, node):
        return node.find_element_by_xpath('..')

    def get_child_nodes(self, node):
        return node.find_elements_by_xpath('./*')

    def save_screenshot(self, path="screenshot.png"):
        self.driver.save_screenshot(path)

    def remove_log_file(self):
        try:
            remove('geckodriver.log')
            return True
        except:
            return False

    def check_log_file(self):
        if path.isfile('geckodriver.log'):
            self.remove_log_file()