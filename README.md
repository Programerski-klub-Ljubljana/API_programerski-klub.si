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
google-chrome htmlcov/index.html
```

```bash
for i in {1..10} ; do echo "-------------------------$i----------------" && python -m unittest test.02_services_tests.test_payment_service; done
```

## TODO:
V token data probaj posiljati _id entitija, saj bo zmeraj unikaten!
