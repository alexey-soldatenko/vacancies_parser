from bs4 import BeautifulSoup
from bs4 import element
import requests
import asyncio
import time
import aiohttp

count = 0
async def query(link):
	'''функция для обработки запроса. 
		Принимает url и возвращает объект BeautifulSoup
		для дальнейшей обработки'''
	headers = {
			'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) \
				Gecko/20100101 Firefox/12.0'}
	async with aiohttp.ClientSession() as session:
		async with session.get(link) as response:
			response = await response.read()
	soup = BeautifulSoup(response.decode('utf-8'), 'html.parser')	
	return soup

def link_to_new_page(base_url, next_page_obj):
	'''функция для определения наличия дополнительных страниц.
		Принимает объект Node, в котором ищется ссылка на 
		следующую страницу с объявлениеми.
		Возвращает None или ссылку на страницу.'''
	if next_page_obj:
		print(1)
		if next_page_obj.name == 'a':
			new_page = base_url + next_page_obj.get('href')
		else:
			if next_page_obj.a:
				new_page = base_url + next_page_obj.a.get('href')
			else:
				new_page = None
	else:
		new_page = None
	return new_page

def text_formatting(tag):
	'''функция для форматирования текста.
		На вход получаем объект Node, из которого извлекается текст.
		Возвращает строку, соотв. тексту Node'''
	text = ''
	for i in tag.children:
		if isinstance(i, element.NavigableString):
			text += i + ' '
		else:
			child = i.children
			if child:
				for j in child:
					if isinstance(j, element.NavigableString):
						text += j + ' ' 
					else:
						if j.name in ['b', 'i', 'span']:
							text += j.get_text() + ' '
						else:
							text += j.get_text() + '<br>'
				text += '<br>'
			else:
				text += i.get_text() + '<br>'

	return text


async def rabota_ua():
	'''фукнция для извлечения данных из https://rabota.ua'''
	base_url = 'https://rabota.ua'
	new_page = base_url +\
	"/jobsearch/vacancy_list?keyWords=python&scheduleId=3&parentId=1"
	out = ''
	global count
	while new_page:
		#заходим на страницу с объявлениями
		soup = await query(new_page)
		divs = soup.findAll('div', attrs={'class':'fd-f1'})
		#проверяем существует ли следующая страница
		next_page = soup.find('dd', attrs={'class':'nextbtn'})
		new_page = link_to_new_page(base_url, next_page)
		for div in divs:
			if div.h3:
				#обрабатываем каждое объявление
				title = div.h3.string.strip() + '\n'
				a = div.h3.a.get('href').strip()
				href = base_url + a
				out += '<div class="title"><a href="{0}">{1} -\
						{2}</a></div>'.format(href, base_url, title)
				#заходим на страницу объявления
				soup = await query(href)
				div = soup.find('div', 
				attrs={'class':'f-vacancy-description-inner-content'})
				
				text = text_formatting(div)
				out += '<div class="text">{}</div>'.format(text)
				count += 1
	return out


	
	
async def work_ua():
	'''фукнция для извлечения данных из https://www.work.ua'''
	base_url = 'https://www.work.ua'
	new_page = base_url +\
	"/jobs-python/?advs=1&sel_zan=76"
	out = ''
	global count
	while new_page:
		#заходим на страницу с объявлениями
		soup = await query(new_page)
		divs = soup.findAll('div', attrs={
								'class':'card card-hover card-visited\
								 wordwrap job-link card-logotype'})
		divs += soup.findAll('div', attrs={
								'class':'card card-hover card-visited\
									 wordwrap job-link'})
		ul = soup.find('ul', attrs={'class':"pagination hidden-xs"})
		#проверяем существует ли следующая страница
		if ul:
			next_page = ul.findAll('li')[-1]
			new_page = link_to_new_page(base_url, next_page)
		else:
			new_page = None
		for d in divs:
			#обрабатываем каждое объявление
			title = d.find('h2').a.string.strip()
			a = d.find('h2').a.get('href')
			href = base_url + a
			out += '<div class="title"><a href="{0}">{1} - \
					{2}</a></div>'.format(href, base_url, title)
			#заходим на страницу объявления
			soup = await query(href)
			div = soup.find('div', attrs={'class':"overflow wordwrap"})
			text = text_formatting(div)
			out += '<div class="text">{}\n</div>'.format(text)
			count += 1


	return out


async def hh_ua():
	'''фукнция для извлечения данных из https://hh.ua'''
	base_url = 'https://hh.ua'
	new_page = base_url +\
	"/search/vacancy?order_by=publication_time&schedule=remote&\
	enable_snippets=true&area=5&text=Python&clusters=true&\
	search_period=7&currency_code=UAH&experience=between1And3&\
	from=cluster_experience"
	out = ''
	global count
	while new_page:
		#заходим на страницу с объявлениями
		soup = await query(new_page)
		divs = soup.findAll('div', 
					attrs={'class':'vacancy-serp-item__info'})
		#проверяем существует ли следующая страница
		next_page = soup.find('a', attrs={
									'class':"bloko-button \
										HH-Pager-Controls-Next \
										HH-Pager-Control"})
		new_page = link_to_new_page(base_url, next_page)
		for d in divs:
			t = d.find('div', 
					attrs={'class':'vacancy-serp-item__title'})
			if t:
				#обрабатываем каждое объявление
				title = t.a.string.strip()
				href = t.a.get('href')
				out += '<div class="title"><a href="{0}">{1} - \
						{2}</a></div>'.format(href, base_url, title)
				#заходим на страницу объявления
				soup = await query(href)
				description = soup.find('div',
								attrs={'class':"g-user-content"})
				if not description:
					description = soup.find('div',
						attrs={'class':'vacancy-branded-user-content'})
				requirements = soup.find('div',
						attrs={'class':"bloko-gap bloko-gap_bottom"})
				text = text_formatting(description)
				out += '<div class="text">{0}\n{1}</div>'.format(
										requirements.get_text(), text)
				count += 1
	return out


async def main(loop):	
	'''функция для обработки 3 сайтов и составления результирующей 
	html-страницы'''
	#обрабатываем сайты
	completed, pending = await asyncio.wait([work_ua(),
											rabota_ua(),
											hh_ua()])
	#создаем результирующую html-страницу
	html = '<html><head><title>Вакансии</title><meta charset="utf-8">\
	<link rel="stylesheet" type="text/css" href="vacancy.css"</head>\
	<body>'
	html += '<div class="count">\
				Найдено объявлений: {}</div>'.format(count)
	#наполняем страницу содержимым
	for item in completed:
		html += item.result()
	html += '</body></html>'
	#записываем полученную страницу в файл
	with open('vacancy.html', 'w') as f:	
		f.write(html)
	
if __name__ == '__main__':
	t = time.time()   
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main(loop))
	loop.close()
	print(time.time()-t)
	print('Всего объявлений:', count)
