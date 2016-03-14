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
    image = "catalog/img/{}.jpg".format(id)
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
 #       price = "Нет в продаже"
        price = 0
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

def get_categ(all):
    #if( all[0] and all[1] and all[2] and all[3]):
        #return "{}|{}|{}|{}".format(all[0].strip(),all[1].strip(),all[2].strip(),all[3].strip())
    if( all[0] and all[1] and all[2]):
        return "{}|{}|{}".format(all[0].strip(),all[1].strip(),all[2].strip())
    elif( all[0] and all[1] ):
        return "{}|{}".format(all[0].strip(),all[1].strip())
    else:
        return "{}".format(all[0].strip())

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
                all_params.append('|')
    #all_params = ''.join(all_params)
    
    # price
    price = price_int(soup)
    # developer
    developer = soup.find('div', class_="producer-icon").a['title']
    # video
    video_tag = get_video(soup)
    item = []
    item.append({
               '_ID_'               : id,
               '_MAIN_CATEGORY_'    : get_categ(all),
               '_MANUFACTURER_'     : developer,
               '_NAME_'             : model,
               '_META_TITLE_'       : model,
               '_META_H1_'          : model,
               '_META_KEYWORDS_'    : "{},{},{},{},купить,спб,в сакнт-петербурге,игодно ру,igodno,магазин систем безопасности".format(all[0].strip(),all[1].strip(),model,developer),
               '_META_DESCRIPTION_' : description[0:255],
               '_DESCRIPTION_'      : description,
               '_SEO_KEYWORD_'      : "{},{},{},{},купить,спб,в сакнт-петербурге,игодно ру,igodno,магазин систем безопасности".format(all[0].strip(),all[1].strip(),model,developer),

               '_PRICE_'            : price,
               '_IMAGE_'            : image
               #'video'      : video_tag
               #'parametres' : all_params,
               #'characts'   : characts,
               
                          })
    #print(item)
    return item
								


def save(items, path):
    with io.open(path, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        #writer.writerow(('_ID_', '_MAIN_CATEGORY_', '_MANUFACTURER_', '_NAME_', '_DESCRIPTION_', 'params', 'characts', '_PRICE_', '_IMAGE_', 'video'))
        writer.writerow((
            '_ID_',
            '_MAIN_CATEGORY_',
            '_MANUFACTURER_',
            '_NAME_',
            '_META_TITLE_',
            '_META_H1_',
            '_META_KEYWORDS_',
            '_SEO_KEYWORD_',
            '_META_DESCRIPTION_',
            '_DESCRIPTION_',
            '_PRICE_',
            '_IMAGE_'))
        writer.writerows(
           (item['_ID_'],
            item['_MAIN_CATEGORY_'],
            item['_MANUFACTURER_'],
            item['_NAME_'],
            item['_META_TITLE_'],
            item['_META_H1_'],
            item['_META_KEYWORDS_'],
            item['_SEO_KEYWORD_'],
            item['_META_DESCRIPTION_'],
            item['_DESCRIPTION_'],
            item['_PRICE_'],
            item['_IMAGE_']) for item in items
           )


def main():
    id_start = 10001 # start
    id = id_start
    id_end = 20000 # end
    count = 0
    
    items = []
    while id < id_end:
        BASE_URL = 'http://videoglaz.ru/good.php?id={}'.format(id)
        count = count + 1
        if( count<2):
            count = 2
        try:
            items.extend(parse(get_html(BASE_URL), id))
        except Exception:
            print("there is no item")
            count = count - 1
        if ( count%251 == 0 ):# it makes every 250 items put into csv
            print('Downloading...{}'.format(count))
            id_start = id - 25
            save(items, 'doc/videoglaz_store_items_{}_to_{}.csv'.format(id_start, id))
            count = 0
            items = []            
        id = id + 1
        if ( id == id_end):
            print('Downloading...{}'.format(count))
            id_start = id - 25
            save(items, 'doc/videoglaz_store_items_{}_to_{}.csv'.format(id_start, id_end))

    print('The end...')


if __name__ == '__main__':
    main()
