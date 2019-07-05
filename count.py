import re
import sys
import asyncio
import argparse
import urllib.parse
from itertools import cycle

import bs4
import aiohttp
import numpy as np


class GeekbenchUrls():

    @classmethod
    def base(cls) -> str:
        return 'http://browser.geekbench.com'

    @classmethod
    def search(cls, keywords, page=None) -> str:
        return f'{cls.base()}/v4/cpu/search?q={keywords}&page={page if page else 1}'

    @classmethod
    def result(cls, num) -> str:
        return f'{cls.base()}/v4/cpu/{num}'

    @classmethod
    def custom(cls, path) -> str:
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


async def fetch(sess, url:str, proxy:str=None, retry:int=3) -> str:
    while True:
        retry -= 1
        response = await sess.get(url, proxy=proxy)
        if response.status == 200 or not retry:
            return await response.text()


async def getResults(args:argparse.Namespace) -> list:

    keywords = urllib.parse.quote(' '.join(tuple(map(str.strip, args.keywords))))
    connector = aiohttp.TCPConnector(limit_per_host=args.n_connections)
    async with aiohttp.ClientSession(connector=connector) as sess:

        print(f'Expecting {args.n_pages} page(s) of results...', end=' ', flush=True)
        urls = tuple(GeekbenchUrls.search(keywords, page) for page in range(1, args.n_pages + 1))
        tasks = map(asyncio.ensure_future, (fetch(sess, url, proxy=proxy, retry=args.n_retry)
                                            for url, proxy in zip(urls, cycle(args.proxy))))
        htmls = await asyncio.gather(*tasks)

        n = args.n_pages
        for i, html in enumerate(htmls):
            if 'Geekbench 4 CPU Search' not in html or 'did not match any' in html:
                n -= 1
                htmls[i] = ''
        print(f'{n} fetched', flush=True)
        if not n:
            sys.exit()

        urls = []
        for html in htmls:
            for td in bs4.BeautifulSoup(html, 'html.parser').find_all('td'):
                if 'model' in td['class']:
                    urls.append(GeekbenchUrls.custom(td.a['href']))
        assert urls, 'ERROR: no result link parsed'

        print(f'Gathering {len(urls)} results...', end=' ', flush=True)
        tasks = map(asyncio.ensure_future, (fetch(sess, url, proxy=proxy, retry=args.n_retry)
                                            for url, proxy in zip(urls, cycle(args.proxy))))
        htmls = await asyncio.gather(*tasks)

        n = len(urls)
        for i, html in enumerate(htmls):
            if 'Result Information' not in html:
                n -= 1
                htmls[i] = ''
        print(f'{n} fetched', end=' ', flush=True)

        if args.with_keywords or args.without_keywords:
            for idx, html in enumerate(htmls):
                for keyword in args.with_keywords:
                    if keyword not in html:
                        htmls[idx] = '';
                        n -= 1
                        break
                for keyword in args.without_keywords:
                    if keyword in html:
                        htmls[idx] = '';
                        n -= 1
                        break
            print(f'-> {n} filtered', end='', flush=True)
        if not n:
            sys.exit()
        print()

        scores = []
        for html in htmls:
            for th in bs4.BeautifulSoup(html, 'html.parser').find_all('th'):
                if 'score' in th['class']:
                    # some `th`s with `class='score'` are not scores
                    try:
                        scores.append(int(th.string))
                    except ValueError:
                        continue
        assert scores and not len(scores) % 10, f'bad number of scores ({len(scores)})'

    return scores


def main(args:argparse.Namespace) -> None:

    scores = asyncio.run(getResults(args))
    scores = np.asarray(scores, dtype=np.int32).reshape(-1, 10)
    st_avg = np.mean(scores[:, 0])
    st_std = np.std(scores[:, 0], ddof=1)
    idx1 = np.where(scores[:, 0] >= st_avg - 1 * st_std)
    idx2 = np.where(scores[:, 0] <= st_avg + 1 * st_std)
    mt_avg = np.mean(scores[:, 5])
    mt_std = np.std(scores[:, 5])
    idx3 = np.where(scores[:, 5] >= mt_avg - 1 * mt_std)
    idx4 = np.where(scores[:, 5] <= mt_avg + 1 * mt_std)
    idx = np.intersect1d(np.intersect1d(idx1, idx2), np.intersect1d(idx3, idx4))
    print(f'Using {len(idx)} results within 1 standard deviation')

    scores = scores[idx]
    st_tot = int(np.mean(scores[:, 0]))
    st_cry = int(np.mean(scores[:, 1]))
    st_int = int(np.mean(scores[:, 2]))
    st_flo = int(np.mean(scores[:, 3]))
    st_mem = int(np.mean(scores[:, 4]))
    mt_tot = int(np.mean(scores[:, 5]))
    mt_cry = int(np.mean(scores[:, 6]))
    mt_int = int(np.mean(scores[:, 7]))
    mt_flo = int(np.mean(scores[:, 8]))
    mt_mem = int(np.mean(scores[:, 9]))

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
        epilog='The maximum number of simultaneous requests to Geekbench seems to be around 5 per IP.\
                Exceeding this number will receive http 429 error. \
                For a higher speed, try a group of load-balanced proxy servers.')
    parser.add_argument('keywords', metavar='keyword', type=str, nargs='+',
                        help='the keywords to search results')
    parser.add_argument('-n', '--number', metavar='int', dest='n_pages',type=int, default=4,
                        help='the number of page of search results to fetch (default: 4)')
    parser.add_argument('-c', '--connections', metavar='int', dest='n_connections', type=int, default=5,
                        help='the number of simultaneous connections (default: 5)')
    parser.add_argument('--retry', metavar='int', dest='n_retry', type=int, default=3,
                        help='the number of connection retries to attempt (default: 3)')
    parser.add_argument('--proxy', metavar='addr:port', dest='proxy', type=str, nargs='+', default=[None],
                        help='the proxies for connections (http only)')
    parser.add_argument('--with', metavar='keyword', dest='with_keywords', type=str, nargs='+', default=[],
                        help='keep a result only if its html has all of these keywords')
    parser.add_argument('--without', metavar='keyword', dest='without_keywords', type=str, nargs='+', default=[],
                        help='remove a result if only its html has any of these keywords')
    main(parser.parse_args())
