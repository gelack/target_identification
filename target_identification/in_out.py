# -*- coding: utf-8 -*-
"""
Created on Wed Sep 02 16:18:02 2015

@author: glackner
"""
import emzed
import os

def load_peakmap(path=None):
    return emzed.io.loadPeakMap(path)
    
def load_peakmaps(pathes=None):
    if not pathes:
            pathes = emzed.gui.askForMultipleFiles(caption='load peakmaps', extensions=['mzML', 'mzXML'])
    return [emzed.io.loadPeakMap(n) for n in pathes]

def get_peaks_table(path):
    return emzed.io.loadCSV(path, sep=';')

def load_result(path):
    result=emzed.io.loadTable(path)
    results=result.splitBy('source')
    for t in results:
        t.title=t.source.uniqueValue()
    return results
    
def save_results_as_single_table(results, path, title='result'):
    ending = 'table'
    result = emzed.utils.mergeTables(results, force_merge=True)
    title='.'.join([title,ending])
    target=os.path.join(path, title)
    emzed.io.storeTable(result, target, forceOverwrite=True)


def save_csv(results, path):
    ending = 'csv'
    for result in results:
        title = result.source.uniqueValue()
        title='.'.join([title,ending])
        target=os.path.join(path, title)
        emzed.io.storeCSV(result, target)

    
def main_save(results, path, title='result'):
    save_results_as_single_table(results, path, title)
    save_csv(results, path)
    emzed.gui.showInformation('Result is saved')
    