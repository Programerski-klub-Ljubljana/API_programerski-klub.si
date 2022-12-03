# API programerski-klub.si

Server programerskega kluba Ljubljana AKA Monster!

## Instalacija

Odpres pycharm in ti prepozna requirements...
In rečeš da hočeš vse inštalirati.

## Zagon

Server poženeš z ukazom, deluje podobno kot deamon.

```bash
uvicorn api.API:fapi.02_services_tests --host 0.0.0.0
```

## Testing

```bash
coverage run -m unittest discover test
```

```bash
coverage html --omit="*/test*,*/core/services/*"
firefox htmlcov/index.html
```


## TODO:
Ali se lahko email v podatkovni bazi podvoji?
Ce nekdo potrdi email in potem spet nekdo isti email potrdi
potem lahko obadva uporabljata isti email vendar pri authentikaciji
se mora potem stvari malce drugace delati, ravno tako pri izpisu potrebujes
se druge informacije razen emaila da lahko izpises mudela.
