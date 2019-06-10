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
Checking keywords... 329574 results exist
Fetching links... OK
Fetching scores... OK
Using 74 of 100 results within 1 standard deviation

    Avg score       st       mt    ratio
    integer :     2593    11410     4.40
    float   :     1989     8108     4.08
    crypto  :     1498     7348     4.91
    memory  :     2509     3036     1.21
    total   :     2340     8541     3.65
```

The one searches for HiSilicon Kirin 710.

```text
$ python count.py ARM implementer 65 architecture 8 variant 0 part 3337 revision 2 --with 1.71 \
--proxy http://127.0.0.1:1080 -n 500 -c 20
Checking keywords... 182343 results exist
Fetching links... OK
Fetching scores... OK
Using 84 of 116 results within 1 standard deviation

    Avg score       st       mt    ratio
    integer :     1772     7201     4.06
    float   :     1191     4921     4.13
    crypto  :     1044     5051     4.84
    memory  :     1800     2029     1.13
    total   :     1567     5375     3.43
```

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>
