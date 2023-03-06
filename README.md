# N26 Plugin for [ofxstatement](https://github.com/kedder/ofxstatement/)

Parses N26 csv statement files to be used with GNU Cash or HomeBank.

It only supports categories the Italian statements yet, but all languages can be
easily supported by adding localized strings to the mapping dictionary.

So, contributions are welcome!

## Installation

You can install the plugin as usual from pip or directly from the downloaded git

### `pip`

    pip3 install --user ofxstatement-n26

### `setup.py`

    python3 setup.py install --user

## Usage
Download your transactions file from the official bank's site and then run

    ofxstatement convert -t n26 n26-csv-transactions.csv n26.ofx
