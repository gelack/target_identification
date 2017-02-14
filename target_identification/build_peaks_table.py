# -*- coding: utf-8 -*-
"""
Created on Tue Sep 01 11:38:16 2015

@author: pkiefer
"""

import emzed
from emzed.core.data_types import PeakMap
import in_out as io



def integrate_table(t):
    return emzed.utils.integrate(t, integratorid='emg_exact', msLevel=1)

def get_user_adducts(polarity="pos"):
    choice = ["positive", "negative"] #create a list of keys
    select=emzed.gui.DialogBuilder("Please choose polarity")\
    .addChoice('Polarity',choice)\
    .show()
    polarity = choice[select]
    if polarity == "positive":
        adducts=emzed.adducts.positive.buildTableFromUserDialog()
    elif polarity == "negative":
        adducts=emzed.adducts.negative.buildTableFromUserDialog() 
    return adducts
    
def add_adducts(compounds, adducts):
    expanded_table=compounds.join(adducts, True)
    expanded_table.removePostfixes()
    return expanded_table


def add_mz(peaks_table, z=None, mz_tol=5e-6):
    t=peaks_table.copy()
    if hasattr(peaks_table, 'mf'): #compute mass, mz and z from molecular formula and adducts
        adducts = get_user_adducts()
        t = add_adducts(t, adducts)
        t.addColumn('mass', t.mf.apply(emzed.mass.of), type_=float, format_='%.5f')
        t.addColumn('mz', (t.mass+t.mass_shift)/t.z, type_=float)
        t.addColumn('mzmin', t.mz-(t.mz*mz_tol), type_=float)
        t.addColumn('mzmax', t.mz+(t.mz*mz_tol), type_=float)
        t.dropColumns('z_signed')
        return t.filter(t.z==z) if z else t 
    else: # when only mz is given in database
        t.addColumn('mzmin', t.mz-(t.mz*mz_tol), type_=float)
        t.addColumn('mzmax', t.mz+(t.mz*mz_tol), type_=float)       
        return t
#######################################################3

def add_rt(table, peakmaps):
    def fun(v):
        try:
            return float(v)
        except:
            return None
    if hasattr(table, 'rtmin') & hasattr(table, 'rtmax'):
        table.replaceColumn("rtmin", table.rtmin.apply(fun), type_=float)
        table.replaceColumn("rtmax", table.rtmax.apply(fun), type_=float)
    else:
        pm=select_peakmap(peakmaps)
        table = define_compound_rts(table, pm)
    return table

def select_peakmap(peakmaps):
    pm_dict = {}
    for pm in peakmaps:
        source = pm.meta['source']
        pm_dict[source] = pm
    choice = pm_dict.keys() #create a list of keys
    choice.sort()
    select=emzed.gui.DialogBuilder("Please choose peakmap for RT definition")\
    .addChoice('Peakmaps',choice)\
    .show()
    select_pm_name = choice[select]
    select_pm = pm_dict[select_pm_name]
    return select_pm



def define_compound_rts(peaks_table, pm):
    t=_add_rt_range_from_peakmap(peaks_table, pm)
    t_int=_set_rt_manually(t)
    t=_add_rts_to_peaks_table(peaks_table, t_int)
    _edit_table(t)
    return t

def _add_rt_range_from_peakmap(table, pm):
    rtmin, rtmax=pm.rtRange()
    t=table.copy()
    t.addColumn('rtmin', rtmin, type_=float)
    t.addColumn('rtmax', rtmax, type_=float)
    t.addColumn('peakmap', pm, type_=PeakMap)
    t.addColumn('source', pm.meta['source'], type_=str)
    return t

def _set_rt_manually(t):
    t_int=emzed.utils.integrate(t, integratorid='max', msLevel=1)
    selected=_filter_for_most_abundant_adduct(t_int)
    emzed.gui.showInformation('PLease adapt RT windows by ...')
    emzed.gui.inspect(selected)
    return selected

def _filter_for_most_abundant_adduct(t_int):
# for each compound select mass trace with highest intensity
    t_int.addColumn('select', t_int.area.max.group_by(t_int.name), type_=float)
    t_int=t_int.filter(t_int.area==t_int.select)
    t_int.dropColumns('select')
    return t_int

def  _add_rts_to_peaks_table(table, t_int):
    colnames=['name', 'rtmin', 'rtmax']
    rt_table=t_int.extractColumns(*colnames)
    return table.join(rt_table, table.name.equals(rt_table.name))

def _edit_table(t):
    t.dropColumns('name__0')
    t.removePostfixes()
   
#####################################################################   
# MAIN FUNCTION



def main_build_peaks_table(peakmaps, mz_tol=5e-6, compound_table_path=None):
    path = compound_table_path
    peaks_table = io.get_peaks_table(path)
    peaks_table = add_mz(peaks_table, mz_tol=mz_tol)
    peaks_table = add_rt(peaks_table, peakmaps)
    return peaks_table

   

#    
