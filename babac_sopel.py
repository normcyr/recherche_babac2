#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
recherche_babac2 - a sopel module to search the Cycle Babac catalog
author: Norm1 <norm@normandcyr.com>

follows the website structure as of 2019-09-21
'''

from sopel.module import commands, example
import recherche_babac2 as rb2
import requests, re

def say_results(bot, search_url, list_products):

    if 1 < len(list_products) <= 10:
        bot.say('{} items were found'.format(len(list_products)))

    elif len(list_products) > 10:
        bot.say('{} items were found. This is a lot for a bot to print. I\'ll get you the first 10 items'.format(len(list_products)))
        bot.say('Here is the URL to get all the results: {}'.format(search_url))
        list_products = list_products[0:10]


    elif len(list_products) == 1:
        bot.say('A single item was found')

    else:
        bot.say('No product found')
        exit(0)

    bot.say('| #Babac | ' + 'Item name'.ljust(45, ' ') + ' | Price    | In stock  |')
    bot.say('| ------ | ' + '-'*45 + ' | -------- | --------- |')
    for item in list_products:
        bot.say('| {} | {} | {}$ | {} |'.format(
          item['sku'],
          item['name'].ljust(45, ' ')[:45],
          item['price'].rjust(7),
          item['stock'].ljust(9),
          ))


@commands('babac')
@example('.babac training wheels')
def babac(bot, trigger):

    '''.babac <item name> - Search Cycle Babac catalog for the item.'''

    config_file = '/home/norm/.sopel/modules/config_babac.yml'

    sku_pattern = re.compile('\d{2}[-]?\d{3}$')  # accept 12-345 or 12345, but not 123456 or 1234
    text_pattern = re.compile('[\w0-9 \"()]+') # accept text, numbers and special characters ", ( and )
    price_pattern = re.compile('\d*[.]\d{2}')

    search_text = trigger.group(2)
    if search_text == None:
        return bot.reply('.babac what? Please specify your query. For example ".babac training wheels"')
        exit(0)
    elif text_pattern.match(search_text):
        bot.say('Searching in the Babac catalog for: {}'.format(search_text))
        search_text = search_text.replace(' ', '+')
    else:
        return bot.reply('Illegal search character(s). Only the characters \", ( and ) are accepted.')
        exit(0)

    base_url = 'https://cyclebabac.com'

    username, password, login_url = rb2.load_config(config_file)

    session = rb2.create_session(username, password, login_url, base_url)
    result_page, single_result = rb2.search_item(session, search_text, base_url)
    search_url = result_page.url
    soup_results = rb2.make_soup(result_page)
    list_products, search_type = rb2.parse_results(soup_results, single_result, search_text, sku_pattern, text_pattern, price_pattern)

    say_results(bot, search_url, list_products)


if __name__ == '__main__':
    babac()
