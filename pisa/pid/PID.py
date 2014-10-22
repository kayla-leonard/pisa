#! /usr/bin/env python
#
# PID.py
#
# Performs the particle ID step of sorting the event map templates
# of the previous stage into tracks vs. cascades. Some fraction of
# CC events is identified as tracks, all others are cascades.
#
# author: Timothy C. Arlen
#         tca3@psu.edu
# author: Sebastian Boeser
#         sboeser@physik.uni-bonn.de
#
# date:   April 10, 2014
#

import logging
from argparse import ArgumentParser, RawTextHelpFormatter

import numpy as np

from pisa.pid.ParamPIDService import ParamPIDService
from pisa.pid.KernelFilePIDService import KernelFilePIDService
from pisa.utils.utils import set_verbosity, check_binning
from pisa.utils.jsons import from_json, to_json
from pisa.resources.resources import find_resource


if __name__ == '__main__':

    #Only show errors while parsing 
    set_verbosity(0)
    parser = ArgumentParser(description='Takes a reco event rate file '
                            'as input and produces a set of reconstructed \n'
                            'templates of tracks and cascades.',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('reco_event_maps', metavar='JSON', type=from_json,
                        help='''JSON reco event rate file with following '''
                        '''parameters:\n'''
                        '''{"nue_cc": {'czbins':[...], 'ebins':[...], 'map':[...]}, \n'''
                        ''' "numu_cc": {...}, \n'''
                        ''' "nutau_cc": {...}, \n'''
                        ''' "nuall_nc": {...} }''')
    parser.add_argument('-m', '--mode', type=str, choices=['param', 'stored'],
                        default='param', help='PID service to use (default: param)')
    parser.add_argument('--param_file', metavar='JSON', type=str,
                        default='pid/V15_pid.json',
                        help='JSON file containing parameterizations '
                        'of the particle ID \nfor each event type.')
    parser.add_argument('--kernel_file', metavar='JSON', type=str, default=None,
                        help='JSON file containing pre-calculated PID kernels')
    parser.add_argument('-o', '--outfile', dest='outfile', metavar='FILE', type=str,
                        action='store',default="pid.json",
                        help='''file to store the output''')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='''set verbosity level''')
    args = parser.parse_args()

    #Set verbosity level
    set_verbosity(args.verbose)

    #Check binning
    ebins, czbins = check_binning(args.reco_event_maps)

    #Initialize the PID service
    if args.mode=='param':
        pid_service = ParamPIDService(ebins, czbins, 
                            pid_paramfile=args.param_file, **vars(args))
    elif args.mode=='stored':
        pid_service = KernelFilePIDService(ebins, czbins, 
                            pid_kernelfile=args.kernel_file, **vars(args))

    #Calculate event rates after PID
    event_rate_pid = pid_service.get_pid_maps(args.reco_event_maps)
    
    logging.info("Saving output to: %s"%args.outfile)
    to_json(event_rate_pid,args.outfile)
