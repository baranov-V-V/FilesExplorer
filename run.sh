#!/usr/bin/bash

addr=`ifconfig | grep "inet " | tail -1 | awk '{print $2}'`
echo $addr
flask --app main run --host=$addr