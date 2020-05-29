from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from getpass import getpass
import time
from random import randint

MAX_WAIT = 5
FB_MAIL = input('Enter login: ')
FB_PASS = getpass('Enter password: ')
with open('users_urls.txt','r') as file:
	USERS_URLS = file.readlines()
	USERS_URLS = (url.rstrip('\n') for url in USERS_URLS)

def wait(fn):
	def modified_fn(*args, **kwargs):
		start_time = time.time()
		while True:
			try:
				return fn(*args, **kwargs)
			except NoSuchElementException:
				if time.time() - start_time > MAX_WAIT:
					return False
				time.sleep(0.5)
	return modified_fn

def get_browser():
	options = Options()
	options.add_argument('--headless')
	browser = webdriver.Firefox(options=options)
	return browser

@wait
def authenticate():
	browser.find_element_by_id('email').send_keys(FB_MAIL)
	browser.find_element_by_id('pass').send_keys(FB_PASS)
	browser.find_element_by_id('u_0_b').click()

@wait
def is_logged():
	browser.find_element_by_id('userNav')
	return True

def print_user_friends_links(user_url):
	user_friends_list_url = get_user_friends_list_url(user_url)
	browser.get(user_friends_list_url)
	print(f'\n[###] {user_url}')
	if is_friends_list_available():
		scroll_to_bottom()
		for link in get_friends_links():
			print(link)
	else:
		print(f'[###] Friends not available.')

def get_user_friends_list_url(user_url):
	if 'profile.php?id=' in user_url:
		return f'{user_url}&sk=friends'
	return f'{user_url}/friends'

@wait
def is_friends_list_available():
	link = browser.find_element_by_xpath("//div[@id='pagelet_timeline_medley_friends']/div/div/div/a[1]")
	if ('friends_all' in link.get_attribute("href")):
		return True
	raise NoSuchElementException

def scroll_to_bottom():
	last_height = browser.execute_script("return document.body.scrollHeight")
	while True:
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
		time.sleep(randint(1,3))
		new_height = browser.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height

def get_friends_links():
	links = browser.find_elements_by_xpath("//div[@id='pagelet_timeline_medley_friends']/div/div/ul/li/div/a[@href]")
	for link in links:
			link = link.get_attribute("href")
			link = link.replace('fref=profile_friend_list&hc_location=friends_tab','')[:-1]
			yield link


if __name__ == '__main__':
	browser = get_browser()
	browser.get('http://www.facebook.com')
	print('[###] Authenticating')
	authenticate()
	if is_logged():
		for user_url in USERS_URLS:
			time.sleep(randint(3,10))
			print_user_friends_links(user_url)
		print('\n[###] Parsing finished')
	else:
		print('\n[###] Wrong credentials')
	browser.quit()