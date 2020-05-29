from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from getpass import getpass
import time
import os
from random import randint
from html_parser import parse_user_data_to_json

MAX_WAIT = 5
FB_MAIL = input('Enter login: ')
FB_PASS = getpass('Enter password: ')
with open('users_urls.txt','r') as file:
	USERS_URLS = file.readlines()
USERS_URLS = (url.rstrip('\n') for url in USERS_URLS)
ABOUT_BLOCKS = {
	'education': 'education',
	'living': 'living',
	'contact': 'contact-info',
	'relationship': 'relationship'
	}

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
	browser = webdriver.Chrome(options=options)
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

def save_about_pages_as_html(user_url):
	user_id = get_user_id_from_url(user_url)
	os.makedirs(f'about_pages/{user_id}', exist_ok=True)
	for block, block_url_end in ABOUT_BLOCKS.items():
		user_about_block_url = get_user_about_block_url(user_url, block_url_end)
		browser.get(user_about_block_url)
		if is_id_loaded('pagelet_timeline_medley_about'):
			with open(f'about_pages/{user_id}/{user_id}_{block}_date.html', 'w', encoding='utf-8') as f:
				f.write(browser.page_source)

def get_user_about_block_url(user_url, block_url_end):
	if 'profile.php?id=' in user_url:
		return f'{user_url}&sk=about&section={block_url_end}'
	return f'{user_url}/about?section={block_url_end}'

@wait
def is_id_loaded(id):
	browser.find_element_by_id(id)
	return True
	
def get_user_id_from_url(user_url):
	return user_url.split('/')[-1].replace('profile.php?id=','')

if __name__ == '__main__':
	browser = get_browser()
	browser.get('http://www.facebook.com')
	print('[###] Authenticating')
	authenticate()
	if is_logged():
		for user_url in USERS_URLS:
			time.sleep(randint(3,10))
			save_about_pages_as_html(user_url)
			user_id = get_user_id_from_url(user_url)
			parse_user_data_to_json(user_id)
		print('\n[###] Parsing finished')
	else:
		print('\n[###] Wrong credentials')		
	browser.quit()