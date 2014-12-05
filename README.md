## Python environment

First, have [pip](https://pip.pypa.io/en/latest/installing.html) installed.

Now install the libraries:

``` shell
sudo pip install -r requirements.txt
```

## Install mongoDB

Download [mongodb](http://www.mongodb.org/downloads) and decompress it.

``` shell
cd /path/to/your/mongodb/bin
mongod --dbpath  /path/to/your/db --bind_ip your_ip --port your_port
```

## Install Anaconda

Download and install [Anaconda](http://continuum.io/downloads).

## Build your own config file

Make a copy of `config.sample.py` and rename it to `config.py`.

Edit `config.py` and feel free to create subclasses that inherit `Config` class.

Fill in the blanks for `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN` and `ACCESS_TOKEN_SECRET`.
These values are from your own [twitter apps](https://dev.twitter.com/).

## Run collector

``` python
python -m collector "Keyword to search" --config YourOwnConfigClassName
```

Replace `YourOwnConfigClassName` to the class you created in `config.py`.

## Analyze

Start ipython notebook to run analyze code.

``` shell
ipython notebook --matplotlib=inline
```

Then access [ipython notebook](http://localhost:8888)
and open `analyze.ipynb`.

## Group Work

#### Lu Wang

* `collector`
* Collecting Data
* Technique Support
* Report
* Presentation

#### Hang Li

* `analyzer`
* Draw plots
* Project Proposal
* Report
* Presentation
