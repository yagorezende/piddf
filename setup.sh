#!/bin/bash
# clone Trustbloc orb
git clone https://github.com/trustbloc/orb.git

# clone fabric
cd fabric
git clone https://github.com/hyperledger/fabric-samples.git
bash install-fabric -s -- -f 2.4.7 -c 1.5.5