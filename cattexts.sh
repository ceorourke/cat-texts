#!/bin/bash
BASEDIR=/home/ubuntu/cat-texts/
source $BASEDIR/env/bin/activate
pip install -r $BASEDIR/requirements.txt
source $BASEDIR/secrets.sh
python $BASEDIR/server.py
