# API programerski-klub.si

Server programerskega kluba Ljubljana AKA Monster!

## Instalacija

Odpres pycharm in ti prepozna requirements...
In rečeš da hočeš vse inštalirati.

## Zagon

Server poženeš z ukazom, deluje podobno kot deamon.

```bash
uvicorn src.__main__:api.app --host 0.0.0.0
```

## Testing

```bash
coverage run -m unittest discover test
```

```bash
coverage report --omit="*/test*"
```
