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


[how to add permission to tg bot for sending messages in tg group](https://gist.github.com/zapisnicar/247d53f8e3980f6013a221d8c7459dc3)