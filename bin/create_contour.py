#!/usr/bin/env python3

import sys
import os
import math

import numpy
import matplotlib.pyplot as plt

sys.path.append('../climatemaps')

import climatemaps
from climatemaps.logger import logger

DATA_OUT_DIR = './website/data'

TYPES = {
    'precipitation': {
        'filepath': 'data/precipitation/cpre6190.dat',
        'conversion_factor': 0.1,  # (millimetres/day) *10
        'config': climatemaps.contour.ContourPlotConfig(0.1, 16, colormap=plt.cm.jet_r, unit='mm/day', logscale=True)
    },
    'cloud': {
        'filepath': 'data/cloud/ccld6190.dat',
        'conversion_factor': 1,
        'config': climatemaps.contour.ContourPlotConfig(0, 100, colormap=plt.cm.jet_r, unit='%')
    },
    'mintemp': {
        'filepath': 'data/mintemp/ctmn6190.dat',
        'conversion_factor': 0.1,
        'config': climatemaps.contour.ContourPlotConfig(-40, 28, colormap=plt.cm.jet, unit='C')
    },
    'meantemp': {
        'filepath': 'data/meantemp/ctmp6190.dat',
        'conversion_factor': 0.1,
        'config': climatemaps.contour.ContourPlotConfig(-30, 30, colormap=plt.cm.jet, unit='C')
    },
    'maxtemp': {
        'filepath': 'data/maxtemp/ctmx6190.dat',
        'conversion_factor': 0.1,
        'config': climatemaps.contour.ContourPlotConfig(-20, 50, colormap=plt.cm.jet, unit='C')
    },
    'diurnaltemprange': {
        'filepath': 'data/diurnaltemprange/cdtr6190.dat',
        'conversion_factor': 0.1,
        'config': climatemaps.contour.ContourPlotConfig(0, 20, colormap=plt.cm.jet, unit='C')
    },
    'wetdays': {
        'filepath': 'data/wetdays/cwet6190.dat',
        'conversion_factor': 0.1,
        'config': climatemaps.contour.ContourPlotConfig(0, 30, colormap=plt.cm.jet_r, unit='days')
    },
    'wind': {
        'filepath': 'data/wind/cwnd6190.dat',
        'conversion_factor': 0.1,
        'config': climatemaps.contour.ContourPlotConfig(0, 10, colormap=plt.cm.jet, unit='m/s')
    },
    'radiation': {
        'filepath': 'data/radiation/crad6190.dat',
        'conversion_factor': 1.0,
        'config': climatemaps.contour.ContourPlotConfig(0, 300, colormap=plt.cm.jet, unit='W/m^2')
    },
    'vapourpressure': {
        'filepath': 'data/vapourpressure/cvap6190.dat',
        'conversion_factor': 0.1,
        'config': climatemaps.contour.ContourPlotConfig(1, 34, colormap=plt.cm.jet, unit='hPa')
    },
}


def main():
    for data_type, settings in TYPES.items():
        # for month in range(1, 13):
        for month in range(1, 2):
            logger.info('create image and tiles for "' + data_type + '" and month ' + str(month))
            latrange, lonrange, Z = climatemaps.data.import_climate_data(settings['filepath'], month, settings['conversion_factor'])
            contourmap = climatemaps.contour.Contour(settings['config'], lonrange, latrange, Z)
            contourmap.create_contour_data(
                DATA_OUT_DIR,
                data_type,
                month,
                figure_dpi=800
            )
    # for month in range(1, 13):
    #     create_optimal_map(month)


def create_optimal_map(month):
    settings = TYPES['precipitation']
    latrange, lonrange, Zpre = climatemaps.data.import_climate_data(settings['filepath'], month, settings['conversion_factor'])

    settings = TYPES['cloud']
    latrange, lonrange, Zcloud = climatemaps.data.import_climate_data(settings['filepath'], month, settings['conversion_factor'])

    settings = TYPES['maxtemp']
    latrange, lonrange, Ztmax = climatemaps.data.import_climate_data(settings['filepath'], month, settings['conversion_factor'])

    for x in numpy.nditer(Zpre, op_flags=['readwrite']):
        if x/16.0 > 1.0:
            x[...] = 0.0
        else:
            x[...] = 1.0 - x/16.0

    for x in numpy.nditer(Ztmax, op_flags=['readwrite']):
        temp_ideal = 22
        x[...] = 1.0 - math.pow((x-temp_ideal)/10.0, 2)

    Zscore_cloud = (100 - Zcloud)/100

    Z = (Zpre + Zscore_cloud + Ztmax) / 3.0 * 10.0

    for x in numpy.nditer(Z, op_flags=['readwrite']):
        x[...] = max(x, 0.0)

    config = climatemaps.contour.ContourPlotConfig(0.0, 9.0, colormap=plt.cm.RdYlGn, unit='')
    contourmap = climatemaps.contour.Contour(config, lonrange, latrange, Z)
    contourmap.create_contour_data(
        DATA_OUT_DIR,
        'optimal',
        month,
        figure_dpi=1000
    )
    print('month done: ' + str(month))


if __name__ == "__main__":
    main()
