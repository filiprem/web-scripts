#!/usr/bin/env python3

"""Extract list of open source licenses from SPDX web page to CSV.

The CSV is written to standard output.
"""

import csv
import sys

import argparse
from bs4 import BeautifulSoup
import requests

ARGS = None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--base-url',
        default='https://spdx.org/licenses',
        help='SPDX License List page URL',
    )
    global ARGS
    ARGS = parser.parse_args()
    html = requests.get(ARGS.base_url).text
    soup = BeautifulSoup(html, 'lxml')
    tables = soup('table')
    dump_licenses_from_table(tables[0])


def get_license_text(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    # <div property="spdx:licenseText" class="license-text"> ... </div>
    ltdiv = soup.find('div', property="spdx:licenseText")
    if ltdiv:
        return ltdiv.get_text(' ', strip=True)
    else:
        return None


def dump_licenses_from_table(t):
    """Dump HTML table into CSV.

    >>> myhtml = '''<table>
    ... <tr> <th>r1h1</th> <th>Head2</th> <th>Head3</th> </tr>
    ... <tr> <td>r2d1</td> <td>R2D2</td> <td>r2d3</td> </tr>
    ... </table>'''
    >>> mytable = BeautifulSoup(myhtml, 'lxml')
    >>> dump_licenses_from_table(mytable)
    r1h1,Head2,Head3
    r2d1,R2D2,r2d3
    """

    csvwriter = csv.writer(sys.stdout)
    for tr in t('tr'):
        row = []
        for th in tr('th'):
            row.append(th.get_text(' ', strip=True))
        for td in tr('td'):
            a = td.find('a')
            license_text = None
            if a and 'licenseText' in a['href']:
                license_text = get_license_text(ARGS.base_url + '/' + a['href'])
            if license_text:
                row.append(license_text)
            else:
                row.append(td.get_text(' ', strip=True))
        csvwriter.writerow(row)


if __name__ == "__main__":
    main()
