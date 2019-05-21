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
Checking keywords...found 43486 results (using 100)
Fetching the urls of results...Success
Fetching the scores of results...Success
Using 92/100 results within 2 standard deviations

    Avg score       st       mt    ratio
    integer :     5038    24860     4.93
    float   :     4917    24174     4.92
    crypto  :     4152    13109     3.16
    memory  :     4561     4977     1.09
    total   :     4862    20090     4.13
```

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>