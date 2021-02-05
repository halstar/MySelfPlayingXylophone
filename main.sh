#!/bin/bash

export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1

pidof pigpiod >/dev/null

if [[ $? -ne 0 ]] ;
then
    sudo pigpiod
fi

python3 main.py
