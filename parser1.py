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
        price = "Товар снят с продажи. К заказу недоступен"
        return price
    price = price.strip()
    price = re.sub('[\s+]', '', price ) # into [ '1', '2', ...]
    price = re.findall('(\d+)', price ) #
    s = map(str,  price)   # ['1','2','3']
    s = ''.join(s)          # '123'
    #s = int(s)              # 123
    return s


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
    #item_card = soup.find('table', class_="good-item-{}".format(id))
    description = soup.find_all('p')[0].text
    characts = soup.find_all('ul')[1]
    bbt_tech = soup.find('table', class_="bbt tech") #bbt tech params.encode('ascii', 'ignore')
    all_params = []
    for row in bbt_tech.find_all('tr'):
        i = 0;
        for col in row.find_all('td'):
            i = i + 1
            all_params.append(col.text)
            if i%2==0:
                all_params.append(';')
    # price
    price = int(price_int(soup))
    # developer
    developer = soup.find('div', class_="producer-icon").a['title']
    # video
    video_tag = get_video(soup)
    item = []
    item.append({
               'id'         : id,
               'category'   : all[0],
               'subcat'     : all[1],
               'type'       : all[2],
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
        writer = csv.writer(csvfile)
        writer.writerow(('id', 'category', 'subcat', 'type', 'developer', 'model', 'description', 'params', 'characts', 'price', 'img', 'video'))
        writer.writerows(
           (item['id'], item['category'], item['subcat'], item['type'], item['developer'], item['model'], item['description'], item['parametres'], item['characts'], item['price'], item['img'], item['video']) for item in items
           )


def main():
    id_start = 129056 # start
    id = id_start
    items = []
    while id < 129060:
        BASE_URL = 'http://videoglaz.ru/good.php?id={}'.format(id)
        items.extend(parse(get_html(BASE_URL), id))
        id = id + 1
    print('Сохранение...')
    save(items, 'videoglaz_store_items_{}_to_{}.csv'.format(id_start, id))




if __name__ == '__main__':
    main()
