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
$ python count.py 8750h
Checking keywords... use 100 of 43520 found results
Fetching the links of results... OK
Fetching the scores of results... OK
Using 93 of 100 results within 2 standard deviations

    Avg score       st       mt    ratio
    integer :     5028    24655     4.90
    float   :     4908    24078     4.91
    crypto  :     4178    13335     3.19
    memory  :     4553     5024     1.10
    total   :     4854    19990     4.12
```

The script takes ~2 minutes to complete due to Geekbench limit.\
The result should be slightly higher than that on Geekbench browser.
It also provides the marks for sub parts.

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>
