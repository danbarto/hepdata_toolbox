# HepData tool collection

## CMSSW for combine

``` shell
cmsRel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git cms-init
cd $CMSSW_BASE/src
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v8.1.0
scramv1 b clean; scramv1 b # always make a clean build

cd $CMSSW_BASE/src
wget https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-https.sh; source sparse-checkout-https.sh
scram b -j 8
```

## WH+MET analysis

