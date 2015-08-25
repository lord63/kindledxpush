# KindleDXPush

[![Latest Version][1]][2]
[![The MIT License][3]][4]

This project was created by [@blahgeek][5], now maintained by [@lord63][6].

## Intro

As we all know, we can use Amazon's free 3G network to deliver our docs, but we need
to manually click the deliver button in the browser. This script is born to rescue
us from this boring thing. Config this script, add it to the `crontab` and you're done.
All your docs will be sent to your kindle automatically.


## Requirement

* Python 2.7
* Requests lib
* BeautifulSoup lib
* Linux platform (I haven't test it on windows)

## Install

    $ sudo pip install kindlepush

## Feature

* It has a log file, you can check which file you've delivered.

* Use sqlite database, don't worry about that a doc will be missed or delivered twice.

* Get pending deliveries.

## Usage

    Usage: kindlepush <command> [option]

    Options:
      -h, --help            output the help menu
      -V, --version         output the version number
      -c, --count [count]   the count of the docs to deliver
      -n, --number [number] show how many logs

    Commands:
      read                  read the log file
      pending               get pending deliveries

first, touch a new file named `kindlepush_config.json` under `/usr/local/bin`, including those:

    {
        "email": "xxxxxx",              # your email
        "password": "xxxxxx",           # your amazon's password
        "directory": "/path/to/save/",  # save log file and database, end with '/'
        "count": 15,                    # check how many docs every time that whether those have been deliverred before, default 15 is one page a time.
        "number": 4                     # the default count of log messages when you read from log file
    }

deliver your doc from your kindle library to your kindle:

    $ kindlepush
    Login...
    Delivering...
    delivering YOUR DOC
    Done. Save to db.
    delivering YOUR DOC
    Done. Save to db.

read the log file to get to know the docs which you have delivered:
(default is 4 messages, you can use `-n NUMBER` to get more information.)

    $ kindlepush read
    2014-09-23 07:40:32,077 [INFO] delivered YOURDOC
    2014-09-23 07:40:33,125 [INFO] delivered YOURDOC
    2014-09-23 07:40:34,183 [INFO] delivered YOURDOC
    2014-09-24 14:12:34,506 [INFO] delivered YOURDOC

get pending deliveries:

    $ kindlepush pending
    Login...
    Pending Deliveries:
            你好
            nice

Get help via `kindlepush -h` and `kindlepush read -h`.

## Wiki

see [wiki](https://github.com/lord63/kindledxpush/wiki)

## License

MIT

[1]: http://img.shields.io/pypi/v/kindlepush.svg
[2]: https://pypi.python.org/pypi/kindlepush
[3]: http://img.shields.io/badge/license-MIT-yellow.svg
[4]: https://github.com/lord63/kindledxpush/LICENSE
[5]: https://github.com/blahgeek
[6]: https://github.com/lord63
