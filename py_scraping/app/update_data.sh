#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

curl -XDELETE 'http://elasticsearch:9200/zaim'

eval "`cat "$DIR/command"`"

curl -XPOST "http://elasticsearch:9200/zaim/scrape-money/_bulk?pretty" --data-binary @$DIR/data.json
