# CountGeekbenchScores

Count the average score of the device specified by keywords.

## Prerequisite

```python
sys.version_info >= (3, 7)
aiohttp
```

---

## Example

```text
$ python count.py 8750h
Checking keywords...found 43350 results (using 1000)
Fetching the urls of results...Success
Fetching the scores of results...Success

    Avg score       st       mt    ratio
    integer :     4540    23203     5.11
    float   :     4399    22762     5.17
    crypto  :     3708    12566     3.39
    memory  :     4311     4849     1.12
    total   :     4410    18868     4.28
```

---

## Reference

Largely inspired by <https://github.com/oleglegun/geekbench-avg-scores>