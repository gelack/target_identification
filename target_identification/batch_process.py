# -*- coding: utf-8 -*-
"""
Created on Wed Sep 02 13:31:11 2015

@author: glackner
"""

#1.extract peaks
#2.Filter for existing adducts
#3.Calculate adduct fractions

#Calculate amounts from external calibration curves

import emzed
import re
import wtbox
from emzed.core.data_types import PeakMap


def extract_peaks(table, pm):
    t = table.copy()
    t.addColumn('peakmap', pm, type_= PeakMap)
    source = pm.meta['source']
    t.addColumn('source', get_sample_name(source), type_ = str)
    return emzed.utils.integrate(t, integratorid='emg_exact', msLevel=1)

def filter_for_existing_adducts(t, min_area=1e2):
    t_filt = t.filter(t.area >= min_area)
    return t_filt
    
def set_title(t, pm):
    source = pm.meta['source']
    t.title = get_sample_name(source)
    
def get_sample_name(source):
    pattern = '\.mz[X]?ML'
    return re.split(pattern, source)[0]
    
def get_table_name(source):
    pattern = '\.table'
    return re.split(pattern, source)[0]
    
def calculate_adduct_fractions(t_calc):
    t_calc.addColumn('total_area', t_calc.area.sum.group_by(t_calc.name), type_= float, format_='%2.2e')
    t_calc.updateColumn('adduct_relative_intensity', (t_calc.area/t_calc.total_area), type_=float, format_='%.2f')
    t_calc.dropColumns('total_area')

def main_batch_process(peaks_table, peakmaps, min_area=1e3):
    results = []
    for pm in peakmaps:
        t=wtbox.feature_extraction.targeted_peaks_ms(pm, peaks_table, min_area)
        results.append(t)
    return results
        
def inspect_and_modify(results):
    emzed.gui.inspect(results)
    new_results = []
    for result in results:  
        calculate_adduct_fractions(result)
        new_result = wtbox.table_operations.update_rt_by_integration(result)
        new_results.append(new_result)
    return new_results