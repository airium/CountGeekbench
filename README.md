# CountGeekbenchScores

Count the average score of the device specified by keywords.

## Prerequisite

```python
sys.version_info >= (3, 7)
aiohttp
numpy
```

---

## Usage

```text
$ python count.py -h
usage: count.py [-h] [-n int] [-c int] [--proxy addr:port [addr:port ...]]
                [--with keyword [keyword ...]] [--without keyword [keyword ...]]
                keyword [keyword ...]

count a device's average score and sub-scores on Geekbench 4.

positional arguments:
  keyword                            the keywords to search results

optional arguments:
  -h, --help                         show this help message and exit
  -n, --number int                   the number of results to fetch (default: 100)
  -c, --connections int              the number of simultaneous connections (default: 5)
  --proxy addr:port [addr:port ...]  the proxies for connections (http only)
  --with keyword [keyword ...]       keep a result only if its html has all of these keywords
  --without keyword [keyword ...]    remove a result if only its html has any of these keywords

The maximum number of simultaneous requests to Geekbench seems to be around 5. Exceeding this number
will receive the http 429 error. For a higher speed, try a group of load-balanced proxy servers.
```

---

## Example

The one searches for Qualcomm Snapdragon 845.

```text
$ python count.py sdm845
Checking keywords... use 200 of 318881 found results
Fetching the links of results... OK
Fetching the scores of results... OK
Using 162 of 200 results within 1 standard deviation

    Avg score       st       mt    ratio
    integer :     2554    11235     4.40
    float   :     1955     7874     4.03
    crypto  :     1467     7227     4.93
    memory  :     2463     2988     1.21
    total   :     2302     8377     3.64
```

The one searches for HiSilicon Kirin 970.

```text
$ python count.py ARM implementer 65 architecture 8 variant 0 part 3337 revision 2 \
--proxy http://127.0.0.1:1080 -n 500 -c 20 --with 1.71
Checking keywords... use 500 of 182156 found results
Fetching the links of results... OK
Fetching the scores of results... OK
Using 96 of 135 results within 1 standard deviation

    Avg score       st       mt    ratio
    integer :     1765     7179     4.07
    float   :     1191     4891     4.11
    crypto  :     1037     5048     4.87
    memory  :     1803     2025     1.12
    total   :     1564     5355     3.42
```

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>
