#!/usr/bin/env bash

# download elasticsearch-6.5.2 and unzip
# check zip file
if [ ! -d "/elsticsearch-6.5.2" ]; then
    if [ ! -f "elasticsearch-6.5.2.zip" ]; then
        echo "Downloading elasticsearch-6.5.2.zip"
        wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.2.zip
        echo "Unzip elasticsearch-6.5.2.zip"
        unzip elasticsearch-6.5.2.zip
    else
        echo "Unzip elasticsearch-6.5.2.zip"
        unzip elasticsearch-6.5.2.zip
    fi
fi

cd elasticsearch-6.5.2
./bin/elasticsearch