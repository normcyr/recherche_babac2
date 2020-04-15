#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
recherche_babac2 - a sopel module to search the Cycle Babac catalog
author: Norm1 <norm@normandcyr.com>

follows the website structure as of 2020-03-03
"""

import requests
from bs4 import BeautifulSoup
import re
import yaml
import argparse
from pathlib import Path
from recherche_babac2 import _version


config_file_path = Path(".") / "config.yml"

sku_pattern = re.compile(
    "\d{2}[-]?\d{3}$"
)  # accept 12-345 or 12345, but not 123456 or 1234
text_pattern = re.compile(
    "[\w0-9 \-]+"
)  # accept text, numbers, but no special character except -
price_pattern = re.compile("\d*[.]\d{2}")


class BabacSearch:

    base_url = "https://cyclebabac.com/"
    login_url = "https://cyclebabac.com/wp-login.php"

    def __init__(self, username, password):

        self.username = username
        self.password = password

    def do_the_search(self, search_text):

        list_products = []
        session, loggedin = create_session(
            self.username, self.password, self.login_url, self.base_url
        )

        if loggedin:
            result_page, single_result = search_item(
                session, search_text, self.base_url
            )
            soup_results, item_page_url = make_soup(result_page)
            list_products, search_type, multiple_pages = parse_results(
                soup_results,
                single_result,
                item_page_url,
                search_text,
                sku_pattern,
                text_pattern,
                price_pattern,
            )

        return list_products, loggedin, multiple_pages, item_page_url


def load_config(config_file_path):

    with config_file_path.open(mode="r") as config_file:
        config_data = yaml.safe_load(config_file)

    username = config_data["username"]
    password = config_data["password"]

    return username, password


def create_session(username, password, login_url, base_url):

    loggedin_confirmation = "wordpress_logged_in_"

    with requests.Session() as session:
        headers = {
            "Cookie": "wordpress_test_cookie=WP+Cookie+check",
            "Referer": base_url,
            "User-Agent": "Atelier Biciklo",
        }
        data = {
            "log": username,
            "pwd": password,
            "wp-submit": "Log In",
        }
        response = session.post(
            login_url, headers=headers, data=data, allow_redirects=False
        )

        if loggedin_confirmation in response.headers["Set-Cookie"]:
            loggedin = True
        else:
            loggedin = False

    return session, loggedin


def search_item(session, search_text, base_url):

    product_cat = ""
    post_type = "product"

    if search_text is not None:
        search_dict = {
            "product_cat": product_cat,
            "post_type": post_type,
            "s": search_text,
        }
    else:
        search_dict = {}

    result_page = session.get(base_url, params=search_dict)

    if result_page.history:
        single_result = True
    else:
        single_result = False

    return result_page, single_result


def make_soup(result_page):

    soup_results = BeautifulSoup(result_page.text, "lxml")
    item_page_url = result_page.url

    return soup_results, item_page_url


def parse_results(
    soup_results,
    single_result,
    item_page_url,
    search_text,
    sku_pattern,
    text_pattern,
    price_pattern,
):

    if single_result:
        multiple_pages = False
        if sku_pattern.match(search_text):
            search_type = "sku_only"
            search_text = search_text[:2] + "-" + search_text[-3:]
        elif text_pattern.match(search_text):
            search_type = "single_text"
        else:
            search_type = "error"
            list_products = None

        list_products = parse_single_result(
            soup_results, item_page_url, search_text, sku_pattern, price_pattern
        )

    else:
        if text_pattern.match(search_text):
            search_type = "multiple_text"
            list_products, multiple_pages = parse_multiple_results(
                soup_results, search_text, sku_pattern, price_pattern
            )
        else:
            search_type = "error"
            list_products = None

    return list_products, search_type, multiple_pages


def parse_single_result(
    soup_results, item_page_url, search_text, sku_pattern, price_pattern
):

    list_products = []

    item_sku = soup_results.find("span", {"class": "sku"}).text
    item_name = soup_results.title.text[:-14]
    item_prices = soup_results.find("p", {"class": "price"})

    if item_prices.find("del") is None:
        item_rebate = False
        item_price = item_prices.find(
            "span", {"class": "woocommerce-Price-amount amount"}
        ).text

    else:
        item_rebate = True
        item_price = item_prices.find_all(
            "span", {"class": "woocommerce-Price-amount amount"}
        )[1].text
        item_price = re.findall(price_pattern, item_price)[0]

    item_price = item_price.strip('$')

    is_instock = (
        soup_results.find("span", {"class": "stock_wrapper"})
        .span.text.lstrip()
        .rstrip()
    )

    if is_instock == "In stock":
        item_instock = "Yes"
    elif is_instock == "Out of stock":
        item_instock = "No"
    else:
        item_instock = "Don't know"

    product_info = build_product_info(
        item_sku, item_name, item_price, item_instock, item_rebate, item_page_url
    )

    list_products.append(product_info)

    return list_products


def parse_multiple_results(soup_results, search_text, sku_pattern, price_pattern):

    list_products = []

    section_products = soup_results.find_all("div", {"class": "kw-details clearfix"})

    number_of_results = soup_results.find(
        "p", {"class": "woocommerce-result-count"}
    ).text
    if "all" in number_of_results:
        multiple_pages = False
    else:
        multiple_pages = True

    for item in section_products:
        product_info = parse_info(item, sku_pattern, soup_results)
        list_products.append(product_info)

    return list_products, multiple_pages


def parse_info(item, sku_pattern, soup_results):

    item_sku = (
        item.find("div", {"class": "mg-brand-wrapper mg-brand-wrapper-sku"})
        .text.lstrip()
        .rstrip()
    )
    try:
        item_sku = re.findall(sku_pattern, item_sku)[0]
    except IndexError:
        item_sku = 'N/A   '
    item_name = (
        item.find("h3", {"class": "kw-details-title text-custom-child"})
        .text.lstrip()
        .rstrip()
    )
    item_prices = item.find("span", {"class": "price"})
    item_page_url = item.parent["href"]

    try:
        if item_prices.find("del") is None:
            item_rebate = False
            item_price = item_prices.find(
                "span", {"class": "woocommerce-Price-amount amount"}
            ).text.strip("$")
        else:
            item_rebate = True
            item_price = item_prices.find_all(
                "span", {"class": "woocommerce-Price-amount amount"}
            )[1].text.strip("$")
            item_price = re.findall(price_pattern, item_price)[0]
    except IndexError:
        item_rebate = False
        item_price = "N/A"

    item_instock = "Don't know"

    is_instock = (
        item.find("div", {"class": "mg-brand-wrapper mg-brand-wrapper-stock"})
        .text.lstrip()
        .rstrip()[20:]
    )
    if is_instock == "In stock":
        item_instock = "Yes"
    elif is_instock == "Out of stock":
        item_instock = "No"
    else:
        item_instock = "Don't know"

    product_info = build_product_info(
        item_sku, item_name, item_price, item_instock, item_rebate, item_page_url
    )

    return product_info


def build_product_info(
    item_sku, item_name, item_price, item_instock, item_rebate, item_page_url
):

    product_info = {
        "sku": item_sku,
        "name": item_name,
        "price": item_price,
        "stock": item_instock,
        "rebate": str(item_rebate),
        "page url": item_page_url,
    }

    return product_info


def print_results(list_products, multiple_pages, item_page_url):

    if list_products is None:
        print("No product found")
        exit(0)

    elif len(list_products) >= 1:

        if len(list_products) == 1:
            print("A single item was found")

        elif len(list_products) > 1 and multiple_pages == False:
            print("{} items were found".format(len(list_products)))

        elif len(list_products) > 1 and multiple_pages == True:
            print("Lots of items were found. Printing the first 24 items")
            print("More results can be inspected here: {}".format(item_page_url))

        print(
            "| #Babac | " + "Description".ljust(45, " ") + " | Price     | In stock? |"
        )
        print("| ------ | " + "-" * 45 + " | --------- | --------- |")

        for item in list_products:
            print(
                "| {} | {} | {}$ | {} |".format(
                    item["sku"],
                    item["name"].ljust(45, " ")[:45],
                    item["price"].rjust(8),
                    item["stock"].ljust(9),
                )
            )

    else:
        print("No product found")
        exit(0)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "search_text",
        help="indicate which term(s) you are using to search in the Babac catalogue",
        default="",
        nargs="+",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + _version.__version__
    )
    args = parser.parse_args()

    search_text = " ".join(args.search_text)

    if re.match(sku_pattern, search_text) or re.match(text_pattern, search_text):
        print("Searching for: '{}'".format(search_text))

        username, password = load_config(config_file_path)
        recherche = BabacSearch(username, password)
        (
            list_products,
            loggedin,
            multiple_pages,
            item_page_url,
        ) = recherche.do_the_search(search_text)
        if loggedin:
            print_results(list_products, multiple_pages, item_page_url)
        else:
            print("Failed login.")
    else:
        print("Please avoid using special characters.")


if __name__ == "__main__":
    main()
