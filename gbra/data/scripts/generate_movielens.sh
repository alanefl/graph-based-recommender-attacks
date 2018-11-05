#! /bin/bash
wget http://files.grouplens.org/datasets/movielens/ml-1m.zip
unzip ml-1m.zip
rm ml-1m.zip

echo 'parsing movielens data'
python parse_movielens.py
mv movielens.graph ../
rm -r ml-1m

echo 'Finished loading movielens!'
