# CountGeekbenchResults

Count the average score of the device specified by keywords.

## Prerequisite

```python
sys.version_info >= (3, 7)
aiohttp
```

---

## Example

```text
$ python count.py 7700k
Checking keywords...found 59304 results (using 1000)
Fetching the urls of results...Success
Fetching the scores of results...Success

    Avg score       st       mt    ratio
    integer :     5842    23577     4.04
    float   :     5790    22690     3.92
    crypto  :     4180    19417     4.65
    memory  :     5715     6114     1.07
    total   :     5718    19417     3.40
```

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>