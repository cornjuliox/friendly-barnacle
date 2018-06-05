# Introduction
This spider was designed to scrape the list of active Foreign Principals off
the fara.gov website (`https://www.fara.gov/quick-search.html`).

`sample_fara_spider_principals.json`, located in the root of the project 
directory contains results from a full run of the Scrapy spider.

Running the spider will produce a file named `fara_spider_principals.json`,
which will be overrwritten each time the spider is run. 

## IMPORTANT NOTES:
- The scraped item contains blank fields ('') whenever data for that field
was not available.
- Dates are ISO 8601-compliant dates created using the isoformat() method
of Python's datetime objects. e.g '2011-01-07T00:00:00'
- Duplicates have been filtered out by Scrapy. At time of writing,
the site lists 539 active foreign principals but 508 are being scraped.
- Autothrottle has been enabled, at factory default settings. This is because
without a delay present, there is a chance that the wrong exhibit URL will be 
inserted into the final item.

# Installation
NOTE: This project was set up using `pyenv virtualenv`, using Python version
3.6.0

1. (Optional) Set up a virtualenv environment, using Python version 3.6
1. `cd` into root of the project directory.
1. Install dependencies by running `pip install -r requrirements.txt`
1. Run spider using `scrapy crawl fara_spider`
1. Output of the program will be a file called `fara_spider_principals.json`

## Running tests
To run the unit tests, `cd` into the project root and run the tests using
`python fara_spider_tests.py`.

Output will be logged to console.

Tests were written using Python 3.6 and the unittest module.
