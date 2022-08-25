# discordLotteryBot

## About

```python
#TODO
```

## How to build

Because the bot requires only a minimal database we're using Sqlite3 which is then mounted to the Docker container.
First we need to create a file for our database.

```sh
	touch db.sqlite
```

We then copy `.env.template` and input our real values to the variables.

```sh
	cp .env.template .env
```

Then we should clone the Anime-Girls-Holding-Programming-Books repo and change the directory name to `anime`.

After that we're going to build the docker image.

```sh
	docker build -t bot .
```


## How to run

From the directory of this repo.
```sh
	docker run -v ${PWD}/db.sqlite:/usr/src/app/db.sqlite -d bot [--name bot]
```
