import re
import sys
import asyncio
import urllib.parse

import aiohttp
import numpy as np

# the pattern to match the number of results from https://browser.geekbench.com/v4/cpu/search?q=<keywords>
NUM_RESULTS_PATTERN = r'<small>(?P<num_results>[0-9]{0,3},?[0-9]{0,3},?[0-9]{0,3},?[0-9]{1,3}) results? found</small>'
# the pattern to match the urls of results from https://browser.geekbench.com/v4/cpu/search?q=<keywords>
RESULT_URL_PATTERN = r'''<a href=['"]/(?P<result>v4/cpu/[0-9]{1,12})['"]>'''
# the pattern to match the score of elements from https://browser.geekbench.com/v4/cpu/<result_id>
SCORE_ELEMENT_PATTERN = r'''<th class=['"]score['"]>(?P<score>[0-9]{1,6})</th>'''
# limit to the most recent 100 results i.e. 4 pages
MAX_NUM_RESULTS = 200
RESULTS_PER_PAGE = 25
# the base url for Geekbench
GEEKBENCH_BASE_URL = 'https://browser.geekbench.com'
# the maximum simultaneous requests to Geekbench
GEEKBENCH_REQUEST_LIMIT = 5

async def fetch(sess, url:str) -> str:
    async with sess.get(url) as response:
        return await response.text()

async def getResults(keywords:str) -> list:
    connector = aiohttp.TCPConnector(limit_per_host=GEEKBENCH_REQUEST_LIMIT)
    async with aiohttp.ClientSession(connector=connector) as sess:

        print('Checking keywords...', end=' ', flush=True)
        html = await fetch(sess, f'{GEEKBENCH_BASE_URL}/v4/cpu/search?q={keywords}')
        match = re.search(NUM_RESULTS_PATTERN, html)
        if match:
            num_all_results = int(match.group('num_results').replace(',', ''))
        else:
            raise ValueError('The regex pattern to find the number of results is INVALID')
        if num_all_results == 0:
            raise ValueError('No result exists for your keywords')
        num_results = min(MAX_NUM_RESULTS, num_all_results)
        print(f'use {num_results} of {num_all_results} found results')

        print('Fetching the links of results...', end=' ', flush=True)
        num_pages = (num_results // RESULTS_PER_PAGE) + (1 if num_results % RESULTS_PER_PAGE else 0)
        list_urls = tuple(f'{GEEKBENCH_BASE_URL}/v4/cpu/search?page={page}&q={keywords}'
                                 for page in range(1, num_pages + 1))
        tasks = map(asyncio.ensure_future, (fetch(sess, url) for url in list_urls))
        list_htmls = await asyncio.gather(*tasks)
        list_htmls = ''.join(list_htmls)
        print('OK')

        print('Fetching the scores of results...', end=' ', flush=True)
        result_urls = re.findall(RESULT_URL_PATTERN, list_htmls)
        result_urls = tuple(f'{GEEKBENCH_BASE_URL}/{url}' for url in result_urls)
        tasks = map(asyncio.ensure_future, (fetch(sess, url) for url in result_urls))
        result_htmls = await asyncio.gather(*tasks)
        result_htmls = ''.join(result_htmls)
        print('OK')

    return re.findall(SCORE_ELEMENT_PATTERN, result_htmls)

def main(keywords:str) -> None:
    if not keywords:
        raise ValueError('Please indicate your keywords for searching')
    keywords = ' '.join(tuple(map(str.strip, keywords)))
    keywords = urllib.parse.quote(keywords)
    results = asyncio.run(getResults(keywords))
    if not results:
        raise ValueError('No result successfully retrieved')

    results = np.asarray(results, dtype=np.int32).reshape(-1, 10)
    st_avg = np.mean(results[:, 0])
    st_std = np.std(results[:, 0], ddof=1)
    idx1 = np.where(results[:, 0] >= st_avg - 1 * st_std)
    idx2 = np.where(results[:, 0] <= st_avg + 1 * st_std)
    mt_avg = np.mean(results[:, 5])
    mt_std = np.std(results[:, 5])
    idx3 = np.where(results[:, 5] >= mt_avg - 1 * mt_std)
    idx4 = np.where(results[:, 5] <= mt_avg + 1 * mt_std)
    idx = np.intersect1d(np.intersect1d(idx1, idx2), np.intersect1d(idx3, idx4))
    if len(idx):
        print(f'Using {len(idx)} of {len(results)} results within 1 standard deviation')
        results = results[idx]
    st_tot = int(np.mean(results[:, 0]))
    st_cry = int(np.mean(results[:, 1]))
    st_int = int(np.mean(results[:, 2]))
    st_flo = int(np.mean(results[:, 3]))
    st_mem = int(np.mean(results[:, 4]))
    mt_tot = int(np.mean(results[:, 5]))
    mt_cry = int(np.mean(results[:, 6]))
    mt_int = int(np.mean(results[:, 7]))
    mt_flo = int(np.mean(results[:, 8]))
    mt_mem = int(np.mean(results[:, 9]))

    print(f'''
    Avg score       st       mt    ratio
    integer : {st_int:>8d} {mt_int:>8d} {mt_int/st_int:>8.2f}
    float   : {st_flo:>8d} {mt_flo:>8d} {mt_flo/st_flo:>8.2f}
    crypto  : {st_cry:>8d} {mt_cry:>8d} {mt_cry/st_cry:>8.2f}
    memory  : {st_mem:>8d} {mt_mem:>8d} {mt_mem/st_mem:>8.2f}
    total   : {st_tot:>8d} {mt_tot:>8d} {mt_tot/st_tot:>8.2f}''')

if __name__ == '__main__':
    main(sys.argv[1:])
