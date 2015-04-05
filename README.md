# LSQ
> Pronounced _Less Q_

## Purpose

Here at Logic Soft, when a customer wants a temporary report, it is usually
written in plain SQL and run on the client side. Since these are temporary in
nature, they are either stored on the developer's machine or in some cases
not stored at all. 

But sometimes, there arises a situation where this query needs to be executed
again and then we all go on a wild goose chase searching for the query. 

The purpose of writing LSQ was to centralize such queries.

## Requirements

- MongoDB (2.4+)
- Python (2.7)

## Installation 

- Start the MongoDB daemon 

        $ mongod 

- Clone LSQ

        $ git clone git@github.com:logicsoftind/LSQ.git

- Change to the directory

        $ cd LSQ

- Set up a virtual environment and activate it

        $ virtualenv env
        $ source env/bin/activate

- Install Python requirements

        $ pip install -r requirements.txt

- Copy the `config.py.sample` to `config.py` and change as required

        $ cp config.py.sample config.py
        $ vim config.py

- Run the app

        $ python app.py

Point your browser to `http://localhost:<port>` and you're good
to go.

## Screenshots

![Landing page](http://i.imgur.com/VBFa3Wd.png)

![Individual Query Page](http://i.imgur.com/XSK11t1.png)

## Roadmap

* Full Text Search
* Version Control
* Access Control
