# CountGeekbenchScores

Count the average score of the device specified by keywords.

## Prerequisite

```python
sys.version_info >= (3, 7)
aiohttp
numpy
```

---

## Example

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

The script takes ~2 minutes to complete due to Geekbench limit.\
The result should be slightly higher than that on Geekbench browser.
It also provides the marks for sub parts.

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>
