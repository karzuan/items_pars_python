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

def get_video(soup):
    try:
        video_tag = soup.find('div', class_="videoreview-icon").img
    except Exception:
        video_tag = 'no video'
    return video_tag

def parse(html, id):
    # object soup
    soup = BeautifulSoup(html, "html.parser")
    # get's image url & save
    categories = soup.find('div', class_="top_nav")
    all = []
    for category in categories.find_all('a')[2:]:
        all.append(category.text)
    model = soup.find('h1', class_="pageHeader good-item-name").text
 
    if (soup.find('td', class_="active-price").text):# the term of the loop
            image = soup.find('meta', property="og:image")['content']  # get's image url
            urllib.request.urlretrieve(image, "items/{}.jpg".format(id)) # image save
            #image = "catalog/img/{}.jpg".format(id)# image save
            if (soup.find('div', class_="videoreview-icon").img):
                video_tag = get_video(soup)
                item = []
                item.append({
                       'id'         : id,
                       'category'   : all[0].strip(),
                       'model'      : model,
                       'video'      : video_tag
                             })
                return item

def save(items, path):
    with io.open(path, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        #w = csv.writer(file(r'test.csv','wb'), delimiter=';')
        writer.writerow(('id', 'Категория', 'Модель', 'видеообзор'))
        writer.writerows(
           (item['id'], item['category'], item['model'], item['video']) for item in items
           )
            


def main():
    id_start = 0 # start
    id = id_start
    id_end = 140000 # end
    items =[]

    while id < id_end:
        BASE_URL = 'http://videoglaz.ru/good.php?id={}'.format(id)
 
        try:
            items.extend(parse(get_html(BASE_URL), id))

        except Exception:
            print("there is no item")
           
        id = id + 1
    print('The end...')
    save(items, 'doc/VIDEOOBZOR_{}_to_{}.csv'.format(id_start, id))


if __name__ == '__main__':
    main()
