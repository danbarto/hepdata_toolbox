#!/usr/bin/env python3
import uproot
import copy
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.CMS)

from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper

template_2D = {
    'independent_variables': [
        {
            'header': {"name": "x-axis", "units": "-"},
            'values': [],
        },
        {
            'header': {"name": "y-axis", "units": "-"},
            'values': [],
        },],
    'dependent_variables': [
        {
            'header': {"name": "covariance", "units": "-"},
            'values': [],
        }

    ]
}

template_1D = {
    'independent_variables': [
        {
            'header': {"name": "x-axis", "units": "GeV"},
            'values': [],
        },
        ],
    'dependent_variables': [
        {
            'header': {"name": "actual values", "units": "GeV"},
            'values': [],
        }

    ]
}

if __name__ == '__main__':

    import argparse

    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--fit', action='store', default='prefit', help="Select fit")
    args = argParser.parse_args()

    # load file
    f_in = "fitDiagnostics.root"
    # old FitDiagnostics used for publication
    #f_in = '/home/users/dspitzba/WH/CMSSW_10_2_9/src/WH_studies/Plots/python/data/fitDiagnostics_800_100_ARC_update.root'
    fd = uproot.open(f_in)

    # get the overall covariance matrix
    # shapes_fit_b/s or shapes_prefit
    # we use shapes_fit_s for Figure 5 (postfit) of the publication, so same for HepData entry
    # covariance matrix should be _prefit_ though
    covar = fd[f'shapes_{args.fit}']['overall_total_covar']

    # can't use the sorting from combine
    # taken from here https://github.com/danbarto/WH_studies/blob/master/Plots/python/signalRegions.py
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

    # sort the indices to make matrix compatible with Figure 5
    indices = [ covar.axes[0].labels().index(r[0]+'_0') for r in regions ]

    cov_matrix = covar.values()[np.expand_dims(indices, axis=1), indices]

    # Print diagonal values for sanity check with Figure 5
    print('Background uncertainties for bins (sqrt of covariance diagonal elements)')
    for i in range(len(regions)):
        print('SR{:.0f} {:s}: {:.2f}'.format(i, regions[i][0], np.sqrt(cov_matrix[i,i])))

    fig, ax = plt.subplots(1,1,figsize=(20,20))

    im = ax.matshow(cov_matrix)
    ax.set_ylabel('Signal Region')
    ax.set_xlabel('Signal Region')  # loc doesn't move the label to a different axis
    for i in range(cov_matrix.shape[0]):
        for j in range(cov_matrix.shape[1]):
            c = cov_matrix[j,i]
            ax.text(i, j, "%.1f"%c, va='center', ha='center')
    cbar = ax.figure.colorbar(im)
    cbar.ax.tick_params(labelsize=24)

    fig.savefig('cov_matrix.png')
    fig.savefig('cov_matrix.pdf')

    X, Y = np.meshgrid(range(len(regions)), range(len(regions)))

    cov_hepdata = copy.deepcopy(template_2D)

    cov_hepdata['independent_variables'][0]['values'] = [ {'value': regions[x][0]} for x in X.flatten() ]
    cov_hepdata['independent_variables'][1]['values'] = [ {'value': regions[x][0]} for x in Y.flatten() ]
    cov_hepdata['dependent_variables'][0]['values'] = [ {'value': round(float(x),2)} for x in cov_matrix.flatten() ]
