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




def add_adducts(compounds, adducts):
    new=compounds.join(adducts, True)
    return new


def add_mz(peaks_table, z=None, mz_tol=5e-6):
    t=peaks_table.copy()
    t.addColumn('mass', t.mf.apply(emzed.mass.of), type_=float, format_='%.5f')
    t.addColumn('mz', (t.mass+t.mass_shift)/t.z, type_=float)
    t.addColumn('mzmin', t.mz-(t.mz*mz_tol), type_=float)
    t.addColumn('mzmax', t.mz+(t.mz*mz_tol), type_=float)
    t.dropColumns('z_signed')
    return t.filter(t.z==z) if z else t 


'''
old funtion  
def add_mz_values(peaks_table, z=None, mztol=0.003):
    c=peaks_table    
    c.addColumn('mass', c.mf.apply(emzed.mass.of), type_=float, format_='%.5f')
    adducts=emzed.adducts.negative.toTable()
    res=c.join(adducts, True)
    res.removePostfixes()
    res.addColumn('mz', (res.mass+res.mass_shift)/res.z, type_=float)
    res.addColumn('mzmin', res.mz-mztol, type_=float)
    res.addColumn('mzmax', res.mz + mztol, type_=float)
    res.dropColumns('z_signed')
    return res.filter(res.z==z) if z else res

'''
    
#######################################################3
def define_compound_rts(peaks_table, pm):
    t=_add_rt_range_from_peakmap(peaks_table, pm)
    t_int=_set_rt_manualy(t)
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

def _set_rt_manualy(t):
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



def main_build_peaks_table(pm, adducts, compound_table_path=None):
    path = compound_table_path
    peaks_table = io.get_peaks_table(path)
    peaks_table = add_adducts(peaks_table, adducts)
    peaks_table.removePostfixes()
    peaks_table = add_mz(peaks_table)
    return define_compound_rts(peaks_table, pm)

   

#    
