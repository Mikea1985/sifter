# -*- coding: utf-8 -*-
# sifter/sifter/query

'''
    --------------------------------------------------------------
    sifter's / mpchecker's orbit_checby module.
    
    Jan 2020
    Matt Payne & Margaret Pan & Mike Alexandersen
    
    This module provides functionalities to evaluate 
    dictionaries of chebyshev-coefficients
    
    We are developing a standardized approach regarding 
    orbit integration and subsequent interpolation using
    chebyshev-coefficients applied to 32-day sectors
    
    *WRITE MORE STUFF*
    
    --------------------------------------------------------------
    '''


# Import third-party packages
# --------------------------------------------------------------
import sys, os
import numpy as np
import operator
from collections import OrderedDict, defaultdict
from astropy_healpix import HEALPix as hp
from functools import lru_cache
import json

import random # only necessary while developing


# Import neighboring packages
# --------------------------------------------------------------
#sys.path.append( os.path.dirname(os.path.realpath(__file__)) )
#import sql



def check_validity( cheby_dict ):
    '''
        Check that the input dictionary has the expected 
        structure / variables 

        I think that I/we need to cater for 2-types of dictionary:
        (a) single-sector dictionaries
        (b) multi-sector dictionaries-of-dictionaries

        inputs:
        -------
        cheby_dict: dictionary
        - multi-sector (dict-of-dicts) to represent orbit using checbshev coeffs
        - see ... for details
        
        return:
        -------
        valid: boolean
        - True if input is valid
        
    '''
    
    
    # Is this a valid single-sector dictionary
    if check_single_sector_validity( cheby_dict ):
        return True
    # Is this a valid multi-level dictionary ?
    else:
        return check_multi_sector_validity( cheby_dict )


def check_single_sector_validity( cheby_dict ):
    '''
        Check whether the input dictionary has the expected
        structure / variables of a SINGLE-SECTOR dictionary
        
        An example is pasted below to aide comprehension
        
        {
        "name": "1944", 
        "t_init": 49760, 
        "t_final": 49792, 
        "x": [244465.07162892047, -4.795812061414727, -4.88760037011824e-05, -9.450376252320755e-12, 4.7892948845701174e-15, 4.8826394593871367e-20, -4.783299420901866e-25], 
        "y": [-836482.904715676, 16.90794855499096, 0.00016922282769496152, -8.223932641793344e-12, -1.7198853957070552e-14, -1.7214110402272943e-19, 1.739459747175297e-24], 
        "z": [80184.93827289087, -1.6132386474315321, -1.619155861851922e-05, 1.7356725519167324e-13, 1.6363774310415676e-15, 1.6424497980314655e-20, -1.6518634504667254e-25], 
        "vx": [4364.8185161695465, -0.0879009728343899, -8.817109792731101e-07, 1.6524216830877022e-14, 8.921547512585386e-17, 8.949265030729895e-22, -9.009739411499051e-27], 
        "vy": [-2751.6975750041033, 0.056005655649352996, 5.581842645445684e-07, -5.89418457087e-14, -5.721007680596395e-17, -5.701979009505037e-22, 5.8029333632453154e-27], 
        "vz": [448.7843092088165, -0.009085492420776744, -9.084423045152489e-08, 5.613743655974416e-15, 9.250959564931443e-18, 9.250009494210746e-23, -9.362877488700637e-28], 
        "covxx": [1.1672950021925413e-07, -2.342768511881258e-12, -2.3547286695595207e-17, -1.9429457370970903e-25, 2.3730430824373915e-27, 2.3851894824362616e-32, -2.3933800636502087e-37], 
        "covxy": [-5.611521032219133e-08, 1.1399415538166368e-12, 1.137476558331536e-17, -1.0161053125775767e-24, -1.1630478999263563e-27, -1.1605827935612762e-32, 1.1786796942326325e-37], 
        "covxz": [1.0105267139778303e-08, -2.0397042295327378e-13, -2.0431290020001503e-18, 7.673029741441885e-26, 2.0731213491075355e-28, 2.0766375217319983e-33, -2.095652594316162e-38], 
        "covyy": [-1.1781647338452167e-07, 2.366706496007191e-12, 2.3775116112926324e-17, 2.5432963232318836e-26, -2.3985756946519475e-27, -2.4095602055928056e-32, 2.4199931795456605e-37], 
        "covyz": [6.120262464698932e-09, -1.2209675296524746e-13, -1.2316579034720484e-18, -6.988301279608926e-26, 1.232238928073619e-28, 1.2430754116861151e-33, -1.2397514972563638e-38], 
        "covzz": [9.762550991163301e-09, -1.9376737309061606e-13, -1.9605897092496163e-18, -1.9014272048421186e-25, 1.9496268896533375e-28, 1.9727616324576733e-33, -1.9576115279111544e-38]
    }
    '''
    # Expected keys & data-types
    expected_keys_and_types = [
                               ("name", str),
                               ("t_init", (int, float, np.int64, np.float64)),
                               ("t_final", (int, float, np.int64, np.float64)),
                               ("x", (list, np.ndarray) ),
                               ("y", (list, np.ndarray) ),
                               ("z",(list, np.ndarray) ),
                               ("vx",(list, np.ndarray) ),
                               ("vy",(list, np.ndarray) ),
                               ("vz",(list, np.ndarray) ),
                               ("covxx",(list, np.ndarray) ),
                               ("covxy",(list, np.ndarray) ),
                               ("covxz",(list, np.ndarray) ),
                               ("covyy",(list, np.ndarray) ),
                               ("covyz",(list, np.ndarray) ),
                               ("covzz",(list, np.ndarray) )
                               ]
                               
    # Check data is as expected
    # Needs to
    # (i) be a dict
    # (ii) have all the necessary keys
    # (iii) have all the correct data types
    return True if  isinstance(cheby_dict , dict ) and \
                    np.all( [ key in cheby_dict and isinstance(cheby_dict[key], typ) for key, typ in expected_keys_and_types ] ) \
                else False

def check_multi_sector_validity( cheby_dict ):
    '''
        Check whether the input dictionary has the expected
        structure / variables of a MULTI-SECTOR dictionary
        
    '''
    # Expected keys & data-types
    expected_keys_and_types = [
                               ("name", str),
                               ("t_init", (int, float, np.int64, np.float64)),
                               ("t_final", (int, float, np.int64, np.float64)),
                               ("sectors", (list, np.ndarray) )
                               ]
        
    # Check data is as expected
    # Needs to
    # (i) be a dict
    # (ii) have all the necessary keys
    # (iii) have all the correct data types
    # (iv) individual-sector dictionaries are all valid
    return =  True if   isinstance(cheby_dict , dict ) and \
                        np.all( [ key in cheby_dict and isinstance(cheby_dict[key], typ) for key, typ in expected_keys_and_types ] ) and \
                        np.all( [ check_single_sector_validity( sector_dict ) for sector_dict in cheby_dict[sectors]] )
            else False


def get_valid_range_of_dates_from_cheby( cheby_dict ):
    '''
        Extract the minimum and maximum dates for
        which the supplied dictionary has valid 
        chebyshev-coefficients
        
        inputs:
        -------
        cheby_dict: dictionary
        - multi-sector (dict-of-dicts) to represent orbit using checbshev coeffs
        - see ... for details
        
        return:
        -------
        start_date : float
         - earliest valid date (time system may be MJD, but is implicit : depends on MPan;'s choice of zero-points ...)
         
        end_date : float
         - latest valid date (time system may be MJD, but is implicit : depends on MPan;'s choice of zero-points ...)
        '''
    return False

def generate_HP_from_cheby( JD , cheby_dict ):
    '''
        Check that the input dictionary has the expected
        structure / variables
        
        inputs:
        -------
        cheby_dict: dictionary
        - multi-sector (dict-of-dicts) to represent orbit using checbshev coeffs
        - see ... for details
        
        return:
        -------
        valid: boolean
        - True if input is valid
        
        '''
    return False

def generate_XYZ_from_cheby( JD , cheby_dict ):
    '''
        Check that the input dictionary has the expected
        structure / variables
        
        inputs:
        -------
        cheby_dict: dictionary
        - multi-sector (dict-of-dicts) to represent orbit using checbshev coeffs
        - see ... for details
        
        return:
        -------
        valid: boolean
        - True if input is valid
        
        '''
    return False

def generate_UnitVector_from_cheby( JD , cheby_dict ):
    '''
        Check that the input dictionary has the expected
        structure / variables
        
        inputs:
        -------
        cheby_dict: dictionary
        - multi-sector (dict-of-dicts) to represent orbit using checbshev coeffs
        - see ... for details
        
        return:
        -------
        valid: boolean
        - True if input is valid
        
        '''
    return False

def generate_RaDec_from_cheby( JD , cheby_dict ):
    '''
        Check that the input dictionary has the expected
        structure / variables
        
        inputs:
        -------
        cheby_dict: dictionary
        - multi-sector (dict-of-dicts) to represent orbit using checbshev coeffs
        - see ... for details
        
        return:
        -------
        valid: boolean
        - True if input is valid
        
        '''
    return False






