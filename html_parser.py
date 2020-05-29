from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
user_info = {'date_parsing': str(datetime.date(datetime.now())) }

def parse_basic_info(soup):
	name_span = soup.find('span', {'id': 'fb-timeline-cover-name'})
	user_info['name'], user_info['surname'], *args = name_span.get_text().split()
	user_info['facebook_url'] = name_span.find('a')['href']
	avatar_div = soup.find('div', {'class': 'photoContainer'})
	user_info['url_image'] = avatar_div.find('img')['src']
	user_info['id_facebook'] = avatar_div.find('a')['href'].split('id=')[-1]

def parse_education_block(about_block_full):
	pagelet_eduwork = about_block_full.find('div', {'id': 'pagelet_eduwork'})
	for div in pagelet_eduwork.find('div').children:
		if 'Работа' in div.find('div').find('span').get_text():
			parse_education_block_1(div)
		elif 'Образование' in div.find('div').find('span').get_text():
			parse_education_block_2(div)

def parse_education_block_1(div):
	user_info['work'] = []
	work_list_ul = div.find('ul')
	for work_li in work_list_ul.children:
		work_info = {}
		work_a = work_li.find_all('a')[-1]
		work_info['company_name'] = work_a.get_text()
		data_hovercard = work_a['data-hovercard']
		work_info['id_company'] = re.search('id=(?P<id>\d+)&', data_hovercard).group('id')
		work_info['company_url'] = work_a['href'].split('?')[0]
		position_div = work_li.find('div', {'class': 'fsm fwn fcg'})
		if position_div:
			position_data = div.find_all(text=True)
			if len(position_data)==1 and not any((m in position_data[0]) for m in months):
				work_info['position'] = position_data[0]
			elif len(position_data)==1 and any((m in position_data[0]) for m in months):
				work_info['work_period'] = position_data[0]
			elif len(position_data)>1 and any((m in position_data[2]) for m in months):
				work_info['position'] = position_data[0]
				work_info['work_period'] = position_data[2]
			if work_info.get('work_period'):
				if 'по настоящее время' in work_info['work_period']:
					work_info['position_status'] = 'Работает'
				else: 
					work_info['position_status'] = 'Работал(a)'
		user_info['work'].append(work_info)

def parse_education_block_2(div):
	user_info['education'] = []
	education_list_ul = div.find('ul')
	for li in education_list_ul.children:
		education_info = {}
		a = li.find_all('a')
		education_info['name_education'] = a[-1].get_text()
		education_info['url_education'] = a[-1]['href']
		div = li.find('div', {'class': 'fsm fwn fcg'})
		if div:
			graduated_data = div.find_all(text=True)
			if 'Год выпуска' in graduated_data[0]:
				education_info['graduated']	= graduated_data[0]
			if len(graduated_data)>1:
				education_info['description_education']	= graduated_data[2]
		user_info['education'].append(education_info)

def parse_living_block(about_block_full):
	living_info = {}
	current_city_li = about_block_full.find('li', {'id': 'current_city'})
	if current_city_li:
		living_info['city_status'] = current_city_li.find('a').get_text()
	hometown = about_block_full.find('li', {'id': 'hometown'})
	if hometown:
		hometown_a = hometown.find('a')
		living_info['name'] = hometown_a.get_text()
		living_info['url_city'] = hometown_a['href'].split('?')[0]
	user_info['main_city'] = living_info

def parse_contact_block(about_block_full):
	pagelet_contact = about_block_full.find('div', {'id': 'pagelet_contact'})
	contacts_ul = pagelet_contact.find('ul')
	for li in contacts_ul.children:
		contact_info = {}
		contact_div = li.find('div')
		if contact_div:
			user_info['contacts'] = []
			contact_div = list(contact_div.children)
			contact_info['contact_type'] = contact_div[0].find('span').get_text()
			contact_info['contact_value'] = contact_div[1].get_text()
			user_info['contacts'].append(contact_info)
	pagelet_basic = about_block_full.find('div', {'id': 'pagelet_basic'})
	for li in pagelet_basic.select('div ul li'):
		if 'Дата рождения' in li.get_text():
			user_info['birthday'] = li.find_all('span')[1].get_text()

def parse_relationship_block(about_block_full):
	relationship_info = {}
	pagelet_relationships = about_block_full.find('div', {'id': 'pagelet_relationships'})
	relations_block = list(pagelet_relationships.children)[0]
	relationship_info['status'] = relations_block.find_all('div')[-1].get_text()
	family_status_div = relations_block.select('div a')
	if family_status_div:
		relationship_info['name'] = family_status_div[-1].get_text()
		data_hovercard = family_status_div[-1]['data-hovercard']
		relationship_info['family_status_id'] = re.search('id=(?P<id>\d+)&', data_hovercard).group('id')
	user_info['family_status'] = relationship_info


def parse_friends(soup):
	about_block_full = soup.find('div', {'id': 'pagelet_timeline_medley_about'})
	about_block_data = list(about_block_full.children)[1]
	about_block_parts = list(about_block_data.find('div').find('ul').children)
	if len(about_block_parts)==2:
		mutual_friends_block = about_block_parts[0]
		mutual_friens_list = mutual_friends_block.select('div div div div div ul li')
		if mutual_friens_list:
			user_info['friends_list_mutual'] = []
			for li in mutual_friens_list:
				mutual_friend = {}
				mutual_friend['facebook_url'] = li.find('a')['href']
				mutual_friend['id_facebook'] = li.find('a')['href'].replace('https://www.facebook.com/','')
				mutual_friend['name'] = li.find('a')['data-tooltip-content'].split()[0]
				mutual_friend['surname'] = li.find('a')['data-tooltip-content'].split()[1]
				mutual_friend['url_image'] = li.find('img')['src']
				user_info['friends_list_mutual'].append(mutual_friend)
		mutual_fiends_span = mutual_friends_block.select('div div div div a span')
		if mutual_fiends_span:
			mutual_friends_quantity = mutual_fiends_span[0].get_text()
			user_info['quantity_friends_mutual'] = mutual_friends_quantity

def get_html_soup(path_to_html):
	with open(path_to_html, 'r', encoding='utf-8') as html:
		html_content = html.read()
	return BeautifulSoup(html_content, 'html.parser')

def parse_user_data_to_json(user_id):
	for block in parse_functions.keys():
		path_to_html = f'about_pages/{user_id}/{user_id}_{block}_date.html'
		soup = get_html_soup(path_to_html)
		about_block_full = soup.find('div', {'id': 'pagelet_timeline_medley_about'})
		parse_functions[block](about_block_full)
	parse_basic_info(soup)
	parse_friends(soup)
	with open(f'about_pages/{user_id}/{user_id}.json', 'w', encoding='utf-8') as f:
		json.dump(user_info, f, ensure_ascii=False)

parse_functions = {
	'education': parse_education_block,
	'living': parse_living_block,
	'contact': parse_contact_block,
	'relationship':parse_relationship_block,
}