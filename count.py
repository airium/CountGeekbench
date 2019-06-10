import re
import sys
import asyncio
import urllib.parse
import argparse
import itertools

import aiohttp
import bs4
import numpy as np


RESULTS_PER_PAGE = 25


class GeekbenchUrls():

    @classmethod
    def base(cls):
        return 'https://browser.geekbench.com'

    @classmethod
    def search(cls, keywords, page=None):
        if page:
            return f'{cls.base()}/v4/cpu/search?q={keywords}&page={page}'
        else:
            return f'{cls.base()}/v4/cpu/search?q={keywords}'

    @classmethod
    def result(cls, num):
        return f'{cls.base()}/v4/cpu/{num}'

    @classmethod
    def custom(cls, path):
        return f'{cls.base()}{path}'


class CustomHelpFormatter(argparse.HelpFormatter):

    def __init__(self, prog):
        super().__init__(prog, max_help_position=50, width=100)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string


async def fetch(sess, url:str, proxy:str=None) -> str:
    async with sess.get(url, proxy=proxy) as response:
        return await response.text()


async def getResults(args:argparse.Namespace) -> list:

    keywords = urllib.parse.quote(' '.join(tuple(map(str.strip, args.keywords))))
    connector = aiohttp.TCPConnector(limit_per_host=args.n_connections)
    async with aiohttp.ClientSession(connector=connector) as sess:

        print('Checking keywords...', end=' ', flush=True)
        html = await fetch(sess, GeekbenchUrls.search(keywords), proxy=args.proxy[0])
        n_str = bs4.BeautifulSoup(html, 'html.parser').find_all('h2')[0].small.string
        n_results = int(n_str.split(' ')[0].replace(',', ''))
        if n_results:
            print(f'found {n_results} results', end=' ', flush=True)
            n_results = min(args.n_results, n_results)
            print(f'and will use {n_results}', flush=True)
        else:
            print(f'\n\nNo result exists for the keywords!', flush=True)
            sys.exit()

        print('Fetching links...', end=' ', flush=True)
        n_pages = (n_results // RESULTS_PER_PAGE) + (1 if n_results % RESULTS_PER_PAGE else 0)
        urls = tuple(GeekbenchUrls.search(keywords, page) for page in range(1, n_pages + 1))
        tasks = map(asyncio.ensure_future, (fetch(sess, url, proxy)
                                            for url, proxy in zip(urls, itertools.cycle(args.proxy))))
        htmls = await asyncio.gather(*tasks)
        print('OK')

        print('Fetching scores...', end=' ', flush=True)
        urls = []
        for html in htmls:
            for td in bs4.BeautifulSoup(html, 'html.parser').find_all('td'):
                if 'model' in td['class']:
                    urls.append(GeekbenchUrls.custom(td.a['href']))
        tasks = map(asyncio.ensure_future, (fetch(sess, url, proxy)
                                            for url, proxy in zip(urls, itertools.cycle(args.proxy))))
        htmls = await asyncio.gather(*tasks)
        for idx, html in enumerate(htmls):
            for keyword in args.with_keywords:
                if keyword not in html:
                    htmls[idx] = '';
                    break
            for keyword in args.without_keywords:
                if keyword in html:
                    htmls[idx] = '';
                    break
        scores = []
        for html in htmls:
            for th in bs4.BeautifulSoup(html, 'html.parser').find_all('th'):
                if 'score' in th['class']:
                    try:
                        scores.append(int(th.string))
                    except ValueError:
                        continue
        print('OK')
    return scores


def main(args:argparse.Namespace) -> None:

    results = asyncio.run(getResults(args))
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

    parser = argparse.ArgumentParser(
        formatter_class=lambda prog: CustomHelpFormatter(prog),
        description='count a device\'s average score and sub-scores on Geekbench 4.',
        epilog='The maximum number of simultaneous requests to Geekbench seems to be around 5. \
                Exceeding this number will receive the http 429 error. \
                For a higher speed, try a group of load-balanced proxy servers.')
    parser.add_argument('keywords', metavar='keyword', type=str, nargs='+',
                        help='the keywords to search results')
    parser.add_argument('-n', '--number', metavar='int', dest='n_results',type=int, default=100,
                        help='the number of results to fetch (default: 100)')
    parser.add_argument('-c', '--connections', metavar='int', dest='n_connections', type=int, default=5,
                        help='the number of simultaneous connections (default: 5)')
    parser.add_argument('--proxy', metavar='addr:port', dest='proxy', type=str, nargs='+', default=[None],
                        help='the proxies for connections (http only)')
    parser.add_argument('--with', metavar='keyword', dest='with_keywords', type=str, nargs='+', default=[],
                        help='keep a result only if its html has all of these keywords')
    parser.add_argument('--without', metavar='keyword', dest='without_keywords', type=str, nargs='+', default=[],
                        help='remove a result if only its html has any of these keywords')
    main(parser.parse_args())
