import os
import requests
from getpass import getpass
from bs4 import BeautifulSoup

HOME_PAGE = "http://www.spoj.com"
ACCOUNT = "http://www.spoj.com/myaccount/"
FILE = "http://www.spoj.com/files/src/save/"

def takeDirectory(path):
	if not os.path.exists(path):
		os.makedirs(path)


with requests.Session() as c:
	Username = raw_input("Username: ")
	Password = getpass("Password: ")

	login_data = dict(login_user=Username,password=Password)
	c.get(HOME_PAGE)
	c.post(HOME_PAGE,data=login_data)
	
	r = c.get(ACCOUNT)
	soup = BeautifulSoup(r.content)
	
	problems = soup.find("table","table table-condensed")
	
	
	links = problems.find_all('a')
	new_dir = os.path.abspath("SPOJ")
	takeDirectory(new_dir)

	for link in links:
		status = c.get(HOME_PAGE+link.get('href'))
		an_soup = BeautifulSoup(status.content)

		
		path = os.path.join(new_dir,link.get_text().encode('utf8'))
		takeDirectory(path)

		for accepted in an_soup.find_all("tr","kol1"):
		
			status = accepted.find("td","statustext text-center")
			sol_id = status.get_text().encode('utf8').strip()
				

			with open(os.path.join(path,sol_id),'w') as solution:
				solution.write(c.get(FILE+sol_id).content)
			




