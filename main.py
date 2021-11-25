from time import sleep
from Browser import Browser

bro = Browser()
bro.load_profile()
bro.start_driver()
bro.load_browser_config()

bro.driver.get("https://www.linkedin.com/uas/login")
bro.wait_load_url("https://www.linkedin.com/uas/login")
bro.linkedin_login()

bro.driver.get("https://www.linkedin.com/mwlite/me/add/position")
bro.wait_load_url("https://www.linkedin.com/mwlite/me/add/position")
sleep(5)

bro.search_job()

bro.close()
