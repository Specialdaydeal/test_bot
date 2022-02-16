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
    timeout = 5
    profile = {}
    driver = {}
    closed = True
    start_time = 0
    COOKIE_FILE_NAME = "cookies.pkl"
    last_key = letters[0]
    db = None

    def __init__(self, mobile):
        self.start_time = datetime.now()
        self.db = sl.connect('my.db')

        gui.FAILSAFE = True
        self.check_log_file()
        self.config["is_mobile"] = mobile

        file = open("last_key.txt", "r")
        self.last_key = file.read().upper().replace("\n", "")

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

    def linkedin_login(self, username, password):
        print("start login")
        gui.moveTo(110, 110)
        gui.click()

        sleep(2)
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
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

    def save_last_key(self, text):
        print(f"{text} saved")
        f = open("last_key.txt", "a")
        f.write(text)
        f.close()

    def close_dialog_mobile(self):
        print("8.1. close dialog mobile")
        if not self.closed and not self.config["login"]:
            button = self.wait_show_element("#cnskx")
            if button:
                self.click(button)
                sleep(1)
                gui.click()
                sleep(randrange(3))

    def add_skill(self, name):
        try:
            cur = self.db.cursor()
            cur.execute('INSERT INTO skill(name) VALUES(?)', (name,))
            self.db.commit()
        except:
            pass

    def add_job_title(self, title):
        try:
            cur = self.db.cursor()
            cur.execute('INSERT INTO jobs(title) VALUES(?)', (title,))
            self.db.commit()
        except:
            pass

    def get_new_job_title(self, last_id):
        try:
            cursor = self.db.cursor()
            cursor.execute('SELECT id,title FROM jobs WHERE id > ? ORDER BY id ASC LIMIT 1', (last_id,))
            return cursor.fetchone()
        except:
            return None

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

    def wait_load_url(self, url):
        try:
            wait = WebDriverWait(self.driver, self.timeout)
            url = wait.until(EC.url_contains(url))
            return url
        except:
            return None

    def get_wait_url(self, url):
        self.driver.get(url)
        return self.wait_load_url(url)

    def search_job(self):
        search_input = self.get_element("#postitle")
        if search_input.is_displayed():
            search_input.click()

        next_search = True
        search_key = self.last_key
        gui.typewrite(search_key[:-1])

        while next_search:
            gui.typewrite(search_key[-1])

            items_len = self.get_job_title()

            if items_len == 20:
                search_key += letters[0]
            else:
                letter_index = 1 + letters.find(search_key[-1])
                while letter_index == len(letters):
                    search_key = search_key[:-1]
                    gui.hotkey("backspace")

                    letter_index = 1 + letters.find(search_key[-1])

                new_key = letters[letter_index]
                search_key = search_key[:-1]
                gui.hotkey("backspace")
                search_key += new_key

    def get_skill(self):
        sleep(0.5)
        spinner = True
        while spinner:
            spinner = self.driver.find_element(By.CLASS_NAME, 'typeahead-input-spinner').is_displayed()

        search_text = self.get_element("#skills-typeahead-input").get_attribute('value')
        element = self.driver.find_element(By.ID, "skills-results-list")
        items = element.find_elements(By.CLASS_NAME, "skill-pill")
        items_len = len(items)
        if items_len == 0:
            return 0
        elif items_len == 1 and search_text.lower() == items[0].text.lower():
            return 0
        else:
            for item in items:
                self.add_skill(item.text)
        print(f"{items_len} added")
        return items_len

    def get_job_title(self):
        sleep(0.5)
        spinner = True
        while spinner:
            spinner = self.driver.find_element(By.CLASS_NAME, 'typeahead-input-spinner').is_displayed()

        element = self.driver.find_element(By.ID, "edit-position-typeahead-results")
        items = element.find_elements(By.CLASS_NAME, "simple-item")
        items_len = len(items)
        if items_len == 0:
            return 0
        else:
            for item in items:
                self.add_job_title(item.text)
        print(f"{items_len} added")
        return items_len

    def search_skill(self):
        search_input = self.get_element("#skills-typeahead-input")
        if search_input.is_displayed():
            search_input.click()

        next_search = True
        search_key = self.last_key
        gui.typewrite(search_key[:-1])

        while next_search:
            gui.typewrite(search_key[-1])

            items_len = self.get_skill()

            if items_len == 20:
                search_key += letters[0]
            else:
                letter_index = 1 + letters.find(search_key[-1])
                while letter_index == len(letters):
                    search_key = search_key[:-1]
                    gui.hotkey("backspace")

                    letter_index = 1 + letters.find(search_key[-1])

                new_key = letters[letter_index]
                search_key = search_key[:-1]
                gui.hotkey("backspace")
                search_key += new_key

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

    def search_job_description(self):
        gui.moveTo(150, 150)
        gui.click()

        last_id = 1
        while last_id < 15571:
            try:
                search_input = self.driver.find_element(By.ID, "searchField")
                search_input.click()

                search_input.send_keys(Keys.COMMAND, "A")
                search_input.send_keys(Keys.DELETE)

                job = self.get_new_job_title(last_id)
                last_id = job[0]

                gui.typewrite(job[1])
                gui.hotkey("enter")

                sleep(3)

                self.get_element(".suggestions ul li:first-child").click()

                items = self.wait_show_element("ul.search-examples-group")
                items = items.find_elements(By.TAG_NAME, "li")
                print(f"{len(items)} item added")

                for item in items:
                    description = item.find_element(By.CLASS_NAME, "example-text").text
                    self.add_job_description(last_id, description)

                self.get_element('.example-editor-block .search-input-section .back-to-titles').click()
                sleep(1)
            except:
                continue

    def search_job_category(self):
        gui.moveTo(150, 150)
        gui.click()

        last_id = 1
        while last_id < 15571:
            try:
                search_input = self.driver.find_element(By.ID, "searchField")
                search_input.click()

                search_input.send_keys(Keys.COMMAND, "A")
                search_input.send_keys(Keys.DELETE)

                job = self.get_new_job_title(last_id)
                last_id = job[0]

                gui.typewrite(job[1])
                gui.hotkey("enter")

                sleep(3)

                category = self.get_element(".suggestions ul li:first-child").text

                self.add_job_category(last_id, category)
            except:
                continue

    def add_job_description(self, last_id, description):
        try:
            if self.get_job_description_count(last_id, description) == 0:
                cur = self.db.cursor()
                cur.execute('INSERT INTO job_description(job_title_id, description) VALUES(?,?)',
                            (last_id, description))
                self.db.commit()
        except:
            pass

    def get_job_description_count(self, last_id, description):
        try:
            cursor = self.db.cursor()
            cursor.execute('SELECT id FROM job_description WHERE id = ? and description = ?', (last_id, description))
            return len(cursor.fetchall())
        except:
            return 0

    def login_rg(self):
        sleep(3)
        self.wait_show_element('#app')
        email = self.get_element('.email-wrap input.form-control')
        email.send_keys('miko@bk.ru')

        password = self.get_element('.password-wrap input.form-control')
        password.send_keys('123456')

        login = self.get_element('.login-group-footer button.button-login')
        login.click()

    def add_job_category(self, last_id, category):
        try:
            cur = self.db.cursor()
            cur.execute('UPDATE job_description SET category=? WHERE job_title_id=?',
                        (category, last_id))
            self.db.commit()
        except:
            pass
