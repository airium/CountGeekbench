# CountGeekbenchScores

Count the average score of the device specified by keywords.

## Prerequisite

```python
sys.version_info >= (3, 7)
aiohttp
beautifulsoup4
numpy
```

---

## Usage

```text
$ python count.py -h
usage: count.py [-h] [-n int] [-c int] [--retry int] [--proxy addr:port [addr:port ...]]
                [--with keyword [keyword ...]] [--without keyword [keyword ...]]
                keyword [keyword ...]

count a device's average score and sub-scores on Geekbench 4.

positional arguments:
  keyword                            the keywords to search results

optional arguments:
  -h, --help                         show this help message and exit
  -n, --number int                   the number of page of search results to fetch (default: 4)
  -c, --connections int              the number of simultaneous connections (default: 5)
  --retry int                        the number of connection retries to attempt (default: 3)
  --proxy addr:port [addr:port ...]  the proxies for connections (http only)
  --with keyword [keyword ...]       keep a result only if its html has all of these keywords
  --without keyword [keyword ...]    remove a result if only its html has any of these keywords

The maximum number of simultaneous requests to Geekbench seems to be around 5 per IP. Exceeding this
number will receive http 429 error. For a higher speed, try a group of load-balanced proxy servers.
```

---

## Example

The one searches for Qualcomm Snapdragon 845.

```text
python count.py sdm845
Expecting 4 page(s) of results... 4 fetched
Gathering 100 results... 100 fetched
Using 77 results within 1 standard deviation

    Avg score       st       mt    ratio
    integer :     2587    11182     4.32
    float   :     1970     7758     3.94
    crypto  :     1487     7285     4.90
    memory  :     2469     2986     1.21
    total   :     2323     8321     3.58
```

The one searches for HiSilicon Kirin 710.

```text
$ python count.py ARM implementer 65 architecture 8 variant 0 part 3337 revision 2 --with 1.71 \
--proxy http://127.0.0.1:4411 -n 2 -c 20
Expecting 2 page(s) of results... 2 fetched
Gathering 50 results... 50 fetched -> 14 filtered
Using 7 results within 1 standard deviation

    Avg score       st       mt    ratio
    integer :     1739     7218     4.15
    float   :     1181     4791     4.06
    crypto  :     1024     5019     4.90
    memory  :     1780     2017     1.13
    total   :     1544     5340     3.46
```

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>
