import sys
import urllib.request # ХЗ
import random
import re # lib separate nums from str
from bs4 import BeautifulSoup # HTML супчик
import csv # save csv
import io



######## COSTOMS

#id = 10008 #random.randrange(2400, 128000) go to main



######## FUNCTIONS

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()

def get_image(soup, id):
    image = soup.find('meta', property="og:image")['content']  # get's image url
    urllib.request.urlretrieve(image, "img/{}.jpg".format(id)) # image save
    image = "img/{}.jpg".format(id)
    return image # return url

def get_video(soup):
    try:
        video_tag = soup.find('div', class_="videoreview-icon").img
    except Exception:
        video_tag = 'no video'
    return video_tag

def price_int(soup):         # ' 123 000 руб. '
    try:
        price = soup.find('td', class_="active-price").text
    except Exception:
        price = "Нет в продаже"
        return price
    price = price.strip()
    price = re.sub('[\s+]', '', price ) # into [ '1', '2', ...]
    price = re.findall('(\d+)', price ) #
    s = map(str,  price)   # ['1','2','3']
    s = ''.join(s)         # '123'
    #s = int(s)            # 123
    return s

def clean_desk(description):
    sep = 'Похожие товары' # separator
    #a = "/n/n######*******!!!!!!!!!DESCRIPTION!!!!!!!!!*******#########/n/n"
    rest = description.split(sep, 1)[0]
    return rest


def parse(html, id):
    # object soup
    soup = BeautifulSoup(html, "html.parser")
    # get's image url & save
    image = get_image(soup, id)
    # category, subcat, type from breadcrumbs
    categories = soup.find('div', class_="top_nav")
    all = []
    for category in categories.find_all('a')[2:]:
        all.append(category.text)
    # model, from h1 tag
    model = soup.find('h1', class_="pageHeader good-item-name").text
    # get the item cart: description, characteristics, params

    description = soup.find_all('p')[0].text
    description = clean_desk(description) # cut text after "Похожие товары"
    characts = soup.find_all('ul')[1].text
    bbt_tech = soup.find('table', class_="bbt tech") #bbt tech params.encode('ascii', 'ignore')
    # [0] - category, [1] - subcat, [2] - type
    all_params = []
    for row in bbt_tech.find_all('tr'):
        i = 0;
        for col in row.find_all('td'):
            i = i + 1
            all_params.append(col.text)
            if i%2==0:
                all_params.append('/')
    # price
    price = price_int(soup)
    # developer
    developer = soup.find('div', class_="producer-icon").a['title']
    # video
    video_tag = get_video(soup)
    item = []
    item.append({
               'id'         : id,
               'category'   : all[0].strip(),
               'subcat'     : all[1].strip(),
               'type'       : all[2].strip(),
               'developer'  : developer,
               'model'      : model,
               'description': description,
               'parametres' : all_params,
               'characts'   : characts,
               'price'      : price,
               'img'        : image,
               'video'      : video_tag
                          })
    #print(item)
    return item


def save(items, path):
    with io.open(path, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        #w = csv.writer(file(r'test.csv','wb'), delimiter=';')
        writer.writerow(('id', 'Категория', 'Подкатегория', 'Тип', 'Производитель', 'Модель', 'Описание', 'Параметры', 'Характеристики', 'Цена', 'изображение', 'видеообзор'))
        writer.writerows(
           (item['id'], item['category'], item['subcat'], item['type'], item['developer'], item['model'], item['description'], item['parametres'], item['characts'], item['price'], item['img'], item['video']) for item in items
           )


def main():
    id_start = 0 # start
    id = id_start
    items = []
    while id < 500:
        BASE_URL = 'http://videoglaz.ru/good.php?id={}'.format(id)
        try:
            items.extend(parse(get_html(BASE_URL), id))
        except Exception:
            print("there is no item")
        id = id + 1
    print('Downloading...')
    save(items, 'doc/videoglaz_store_items_{}_to_{}.csv'.format(id_start, id))




if __name__ == '__main__':
    main()
