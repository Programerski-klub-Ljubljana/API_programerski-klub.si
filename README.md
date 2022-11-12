# API programerski-klub.si

Server programerskega kluba Ljubljana AKA Monster!

# Instalacija

Odpres pycharm in ti prepozna requirements...
In rečeš da hočeš vse inštalirati.

# Zagon

Server poženeš z ukazom, deluje podobno kot deamon.

```bash
uvicorn api.__main__:app --host 0.0.0.0 
```

# Arhitektura
```
src
├── api.py
├── db.py
├── env.py
├── __main__.py
├── migration
├── models
│   ├── Clan.py
│   ├── Dogodek.py
│   ├── Ekipa.py
│   ├── Log.py
│   ├── Naloga.py
│   ├── Objava.py
│   ├── Oseba.py
│   ├── Placilo.py
│   ├── __pycache__
│   ├── Sporocilo.py
│   └── Udelezenec.py
├── __pycache__
├── seed
├── services
│   ├── email.py
│   └── __pycache__
└── utils.py
```
