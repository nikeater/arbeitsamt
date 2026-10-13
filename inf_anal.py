import sqlite3
import yaml
import pandas as pd

voll = yaml.safe_load(open("config.yaml", encoding="utf-8"))
l_conn = sqlite3.connect(voll['LevelDb'])
cpu_only = pd.read_sql("SELECT * FROM einstufung WHERE check_id<11152", l_conn)
man_fill = pd.read_sql("SELECT * FROM einstufung WHERE check_id>=11152 AND check_id < 11442", l_conn)
auto_fill = pd.read_sql("SELECT * FROM einstufung WHERE check_id>=11442", l_conn)

print(f" Durchschnittliche Inferenzzeit CPU: {cpu_only.inference_time.mean()}, n={len(cpu_only)}")
print(f" Durchschnittliche Inferenzzeit Fill-Manuell: {man_fill.inference_time.mean()}, n={len(man_fill)}")
print(f" Durchschnittliche Inferenzzeit Fill-Auto: {auto_fill.inference_time.mean()}, n={len(auto_fill)}")
