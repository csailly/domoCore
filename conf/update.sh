#!/bin/bash

path=`dirname $0`
cd ${path}
cd ..

git fetch origin
git reset --hard origin/master
git clean -dfx

exit 0