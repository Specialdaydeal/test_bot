from Browser import Browser

bro = Browser(mobile=False)

bro.load_profile()
bro.start_driver()
bro.load_browser_config()

# bro.get_wait_url("https://www.linkedin.com/uas/login")
#
# username = input("enter linkedin username:\n")
# password = input("enter linkedin password:\n")
#
# bro.linkedin_login(username, password)

# bro.get_wait_url("https://www.linkedin.com/mwlite/me/edit/skills/new")
#
# bro.search_skill()

bro.driver.get("https://app.resumegenius.com/dashboard/account/login")
bro.login_rg()

command = input("press 1 to continue 0 for exit:\n")
if command == "1":
    bro.search_job_category()

bro.close()
