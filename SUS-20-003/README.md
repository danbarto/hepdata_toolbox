# SUS-20-003 (WH+MET)

To pack all yaml files for submission:
```
tar -czvf submission.tgz *.yaml
```

Validate
```
hepdata-validate -a submission.tgz
```

Link to hepdata validation tools: [documentation](https://hepdata-validator.readthedocs.io/en/latest/#command-line)

## Published Figures

Figure 5 produced with this script: [signalRegions.py](https://github.com/danbarto/WH_studies/blob/master/Plots/python/signalRegions.py).

Limit extraction produced with ...

[xsecs](https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections13TeVn2x1wino)

## Covariance matrix

Latest cards are in `/home/users/dspitzba/WH/wh_draw/statistics/unblind_dataCRfix_newSF_allSystUpdate/datacards_updated_withSignalSyst`.

Get FitDiagnostics:

``` shell
combine --forceRecreateNLL -M FitDiagnostics --saveShapes --saveNormalizations --numToysForShape 500 --saveOverall --saveWithUncertainties datacard_mChi-800_mLSP-100__.txt
```
closes with published values.

We need the prefit covariance matrix, just run `python covariance.py`
