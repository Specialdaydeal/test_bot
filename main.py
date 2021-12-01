from Browser import Browser

bro = Browser()
bro.load_profile()
bro.start_driver()
bro.load_browser_config()

bro.driver.get("https://www.linkedin.com/uas/login")
bro.wait_load_url("https://www.linkedin.com/uas/login")

username = input("enter linkedin username:\n")
password = input("enter linkedin password:\n")

bro.linkedin_login(username, password)

# bro.driver.get("https://www.linkedin.com/mwlite/me/add/position")
# bro.wait_load_url("https://www.linkedin.com/mwlite/me/add/position")
#
# bro.search_job()

bro.driver.get("https://www.linkedin.com/mwlite/me/edit/skills/new")
bro.wait_load_url("https://www.linkedin.com/mwlite/me/edit/skills/new")

bro.search_skill()

bro.close()
