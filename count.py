import sys
import time
import re
import itertools
import argparse
import asyncio
import urllib.parse

import aiohttp


# the number of samples up to about 1e12
NUM_RESULTS_PATTERN = r'''<small>(?P<num_results>[0-9]?[0-9]?[0-9]?,[0-9]?[0-9]?[0-9]?,?[0-9]?[0-9]?[0-9]?,?[0-9]?[0-9]?[0-9]) results found</small>'''
RESULT_URL_PATTERN = r'''<a href=['"](?P<result>/v4/cpu/[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9])['"]>'''
# the score up to about 1e6
SCORE_ELEMENT_PATTERN = r'''<th class=['"]score['"]>(?P<score>[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9])</th>'''
# limit to the most recent 40 pages, i.e. 1000 samples
MAX_NUM_PAGES = 40
RESULTS_PER_PAGE = 25


async def fetch(sess, url:str) -> str:
    async with sess.get(url) as response:
        return await response.text()


async def getSamples(keywords: str) -> list:
    async with aiohttp.ClientSession() as sess:

        print('Checking keywords...', end='')
        html = await fetch(sess, f'https://browser.geekbench.com/v4/cpu/search?q={keywords}')
        match = re.search(NUM_RESULTS_PATTERN, html)
        if match:
            num_results = int(match.group('num_results').replace(',', ''))
        else:
            raise ValueError('The regex pattern to find the number of results is INVALID')
        if not num_results:
            raise ValueError('No result exists for your keywords')
        num_pages = min(MAX_NUM_PAGES, num_results / RESULTS_PER_PAGE)
        print(f'found {num_results} results (using {num_pages * RESULTS_PER_PAGE})')

        print('Fetching the urls of results...', end='')
        result_list_urls = \
            tuple(f'https://browser.geekbench.com/v4/cpu/search?page={page}&q={keywords}'
                  for page in range(1, num_pages + 1))
        tasks = map(asyncio.ensure_future, (fetch(sess, url) for url in result_list_urls))
        result_list_htmls = await asyncio.gather(*tasks)
        result_list_htmls = ''.join(result_list_htmls)
        print('Success')

        print('Fetching the scores of results...', end='')
        result_urls = re.findall(RESULT_URL_PATTERN, result_list_htmls)
        result_urls = tuple(f'https://browser.geekbench.com/{url}' for url in result_urls)
        tasks = map(asyncio.ensure_future, (fetch(sess, url) for url in result_urls))
        result_htmls = await asyncio.gather(*tasks)
        result_htmls = ''.join(result_htmls)
        print('Success')

    return re.findall(SCORE_ELEMENT_PATTERN, result_htmls)


def main(keywords):
    if not keywords:
        raise ValueError('Please indicate your keywords for searching')
    keywords = ' '.join(tuple(map(str.strip, keywords)))
    keywords = urllib.parse.quote(keywords)
    results = asyncio.run(getSamples(keywords))
    if not results:
        raise ValueError('No result succussfully retrieved')
    num, rem = divmod(len(results), 10)
    assert rem == 0
    st_tot = sum(map(int, results[0::10])) // num
    st_cry = sum(map(int, results[1::10])) // num
    st_int = sum(map(int, results[2::10])) // num
    st_flo = sum(map(int, results[3::10])) // num
    st_mem = sum(map(int, results[4::10])) // num
    mt_tot = sum(map(int, results[5::10])) // num
    mt_cry = sum(map(int, results[5::10])) // num
    mt_int = sum(map(int, results[7::10])) // num
    mt_flo = sum(map(int, results[8::10])) // num
    mt_mem = sum(map(int, results[9::10])) // num
    print(f'''
    Avg score       st       mt    ratio
    integer : {st_int:>8d} {mt_int:>8d} {mt_int/st_int:>8.2f}
    float   : {st_flo:>8d} {mt_flo:>8d} {mt_flo/st_flo:>8.2f}
    crypto  : {st_cry:>8d} {mt_cry:>8d} {mt_cry/st_cry:>8.2f}
    memory  : {st_mem:>8d} {mt_mem:>8d} {mt_mem/st_mem:>8.2f}
    total   : {st_tot:>8d} {mt_tot:>8d} {mt_tot/st_tot:>8.2f}''')


if __name__ == '__main__':
    main(sys.argv[1:])
