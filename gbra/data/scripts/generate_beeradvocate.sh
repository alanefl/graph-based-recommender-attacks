#! /bin/bash
pushd "$(dirname "$0")"
wget https://snap.stanford.edu/data/Beeradvocate.txt.gz
gunzip Beeradvocate.txt.gz

echo 'parsing data'
python parse_beeradvocate.py
mv beeradvocate.dat* ../
rm Beeradvocate.txt

echo 'Finished loading beeradvocate!'
popd