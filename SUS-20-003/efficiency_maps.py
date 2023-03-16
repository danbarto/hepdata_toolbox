#!/usr/bin/env python3
import glob
import copy
import uproot
import numpy as np
import pandas as pd
from uncertainties import unumpy

from yaml import load, dump
from yaml import Loader, Dumper

template_2D = {
    'independent_variables': [
        {
            'header': {"name": "M_CHI", "units": "GeV"},
            'values': [],
        },
        {
            'header': {"name": "M_LSP", "units": "GeV"},
            'values': [],
        },],
    'dependent_variables': [
        {
            'header': {"name": "efficiency", "units": "-"},
            'values': [],
        }

    ]
}

def get_xsec(mass, model='c1n2'):
    with uproot.open('data/xsec_tchi_13TeV.root') as f:
        h = f[f'h_xsec_{model}'].to_hist()
        return(h.values()[h.axes[0].index(mass)])

def get_masses_from_name(name):
    mchi = int(name.split('mChi-')[-1].split('_mLSP')[0])
    mlsp = int(name.split('mLSP-')[-1].split('_')[0])
    return mchi, mlsp

def get_signal_value(f, region):
    try:
        return f[f'shapes_prefit/{region}/total_signal'].values()
    except:
        return np.array([0.])

def get_signal_variance(f, region):
    try:
        return f[f'shapes_prefit/{region}/total_signal'].variances()
    except:
        return np.array([0.])

def run_fd(
        card,
        regions,
        combine_dir='/home/users/dspitzba/hepdata_toolbox/CMSSW_10_2_13/src/'):
    '''
    Does max likelihood fits
    '''
    import uuid, os, shutil
    import uproot, copy
    ustr          = str(uuid.uuid4())
    uniqueDirname = os.path.join(combine_dir, ustr)
    print("Creating %s"%uniqueDirname)
    os.makedirs(uniqueDirname)
    combineCommand  = f"cd {uniqueDirname};eval `scramv1 runtime -sh`;combine -M FitDiagnostics --robustHesse 1 --forceRecreateNLL --saveShapes --saveNormalizations --saveOverall --saveWithUncertainties {card}"
    os.system(combineCommand)

    with uproot.open(uniqueDirname+"/fitDiagnostics.root") as f:
        values = np.concatenate([ get_signal_value(f, r[0]) for r in regions])
        variances = np.concatenate([ get_signal_variance(f, r[0]) for r in regions])

    shutil.rmtree(uniqueDirname)
    return values, variances



if __name__ == '__main__':
    import argparse

    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--rerun', action='store_true', help="Rerun fitdiagnostics")
    args = argParser.parse_args()

    lumi = 137.2

    regions = [\
        ('nj2_lowmet_res',   2, 0, '125--200'),
        ('nj2_medmet_res',   2, 0, '200--300'),
        ('nj2_highmet_res',  2, 0, '300--400'),
        ('nj2_vhighmet_res', 2, 0, '$>400$'),
        ('nj2_lowmet_boos',  2, 1, '125--300'),
        ('nj2_medmet_boos',  2, 1, '$>300$'),
        ('nj3_lowmet_res',   3, 0, '125--200'),
        ('nj3_medmet_res',   3, 0, '200--300'),
        ('nj3_highmet_res',  3, 0, '300--400'),
        ('nj3_vhighmet_res', 3, 0, '$>400$'),
        ('nj3_lowmet_boos',  3, 1, '125--300'),
        ('nj3_medmet_boos',  3, 1, '$>300$')
    ]
    region_names = [r[0] for r in regions]

    card_dir = '/home/users/dspitzba/WH/wh_draw/statistics/unblind_dataCRfix_newSF_allSystUpdate/datacards_updated_withSignalSyst'
    card_files = glob.glob(card_dir+'/*.txt')

    if args.rerun:
        results = []

        for card in card_files:
            mchi, mlsp = get_masses_from_name(card)
            xsec = get_xsec(mchi)
            values, variances = run_fd(card, regions)
            total_signal = lumi * xsec

            print(sum(values)/total_signal)
            print(values/total_signal)

            signal = unumpy.uarray(values, np.sqrt(variances))

            res = {regions[i][0]: signal[i] for i in range(len(regions))}
            res.update({
                'mchi': mchi,
                'mlsp': mlsp,
                'xsec': xsec,
                'total': xsec*lumi,
            })

            results.append(res)


        df = pd.DataFrame(results)

        df.to_pickle('efficiencies.pkl')
    else:
        df = pd.read_pickle('efficiencies.pkl')

    efficiencies = df[region_names].sum(axis=1)/(df.xsec*1000*lumi*0.6*0.3)

    values_for_hepdata = [{'errors':[{'symerror': float("%.2g" % e.s)}], 'value': float("%.2g" % e.n)} for e in efficiencies]

    hepdata = copy.deepcopy(template_2D)

    hepdata['independent_variables'][0]['values'] = [ {'value': x} for x in df.mchi ]
    hepdata['independent_variables'][1]['values'] = [ {'value': x} for x in df.mlsp ]
    hepdata['dependent_variables'][0]['values'] = values_for_hepdata

    f_out = 'efficiency.yaml'
    with open(f_out, 'w') as f:
        dump(hepdata, f, Dumper=Dumper)

    for region in regions:
        efficiencies = df[[region[0]]].sum(axis=1)/(df.xsec*1000*lumi*0.6*0.3)

        values_for_hepdata = [{'errors':[{'symerror': max(float("%.2g"%e.s), 1e-6)}], 'value': float("%.2g" % e.n)} for e in efficiencies]

        hepdata = copy.deepcopy(template_2D)

        hepdata['independent_variables'][0]['values'] = [ {'value': x} for x in df.mchi ]
        hepdata['independent_variables'][1]['values'] = [ {'value': x} for x in df.mlsp ]
        hepdata['dependent_variables'][0]['values'] = values_for_hepdata

        f_out = f'efficiency_{region[0]}.yaml'
        with open(f_out, 'w') as f:
            dump(hepdata, f, Dumper=Dumper)

        submission_block = \
f'''---
# Start a new YAML document to indicate a new data table.
name: "Efficiency map (SR {region[0]})"
''' + \
'''location: Additional data
description: .
keywords: # used for searching, possibly multiple values for each keyword
  - {name: reactions, values: [P P --> chi chi]}
  - {name: observables, values: [SIG]}
  - {name: cmenergies, values: [6500.0]} # centre-of-mass energy in GeV
  - {name: phrases, values: [electroweakino, chargino, neutralino]}
'''
        file_block = f"data_file: efficiency_{region[0]}.yaml"
        print(submission_block+file_block)
