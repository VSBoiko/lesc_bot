```python
import subprocess as sbp

pkgs = eval(str(sbp.run("pip3 list -o --format=json", shell=True,
                         stdout=sbp.PIPE).stdout, encoding='utf-8'))
for pkg in pkgs:
    sbp.run("pip3 install --upgrade " + pkg['name'], shell=True)
```


```bash
pip install pip-autoremove
pip-autoremove Flask -y
```