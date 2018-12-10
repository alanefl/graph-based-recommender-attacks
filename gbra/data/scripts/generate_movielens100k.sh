#! /bin/bash
pushd "$(dirname "$0")"
wget http://files.grouplens.org/datasets/movielens/ml-100k.zip
unzip ml-100k.zip
rm ml-100k.zip

echo 'parsing movielens data'
python parse_movielens.py 100k
mv movielens_100k.dat* ../
rm -r ml-100k

echo 'Finished loading movielens 100k!'
popd
