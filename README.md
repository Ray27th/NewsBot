# NewsBot

```shell
pip install pipenv
```

```shell
pipenv install
```

## Local

```shell
pipenv run fastapi dev
```

## Deployment

Install fly

```shell
flyctl
```

Redeploy

```shell
flyctl deploy
```

If there are duplicated responses [Due to multiple vm start ups]

```shell
flyctl scale count 1
```

Check status of application

```shell
flyctl status
```
