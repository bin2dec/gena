GenA
====

GenA is a universal static site generator. It's written in [Python](http://www.python.org/).

Installation
------------

GenA is currently under development, but it already has basic functionality. You can use it right now!
Install the latest stable release

    pip install git+https://gitlab.com/dec0der/gena@master

Or if you are a developer, do

    git clone https://gitlab.com/dec0der/gena.git

Usage
-----

    gena [-s SETTINGS] [source] [destination]

Where *SETTINGS* is your settings file, *source* is the directory that contains source files,
and *destination* is the directory for processed files.
All arguments are optional though. That is, if the current directory contains the *settings.py* file and
the *src* subdirectory, then you can run GenA like that:

    gena

In this case, the processed files will be placed in the *dist* subdirectory.
You can also set *source* and *destination* in your settings (*SRC_DIR* and *DST_DIR* respectively).

Examples
--------

Take a look at some examples of using GenA [here](https://gitlab.com/dec0der/gena-examples).
