#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My command line interface
ECE 584 Antenna Theory and Design
Midterm Project
@Author: Ethan Ross
"""

from .arrays import *
import sys
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import warnings

def main():

    # Suppress pesky warning on chebwin() call
    warnings.filterwarnings('ignore', category = UserWarning)

    description = \
"""
Program which plots the array factor and power pattern of an N element
antenna array with spacing, phase, and amplitude defined by the user.

example usage:
python cli.py uniform -N 10 -A 1 -d 0.5 -b -90 --file --no-plots
python cli.py binomial -N 10 -A 1 -d 0.5 --file --no-plots
python cli.py chebyshev -N 10 -A 1 -d 0.25 -R 20
"""

    parser = argparse.ArgumentParser(prog = 'python program.py', description = description,
                                     formatter_class = argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(title = 'Commands', dest = 'arrtype')

    # Uniform parser
    uniform_description = \
"""Define a uniform linear antenna array.
"""

    uniform_parser = subparsers.add_parser('uniform', help = 'define a uniform array',
                                           description = uniform_description,
                                           formatter_class = argparse.RawDescriptionHelpFormatter)
    uniform_parser.add_argument("--no-plots", action = 'store_true', help = 'flag to skip plots')
    uniform_parser.add_argument("--file", action = 'store_true', help = 'flag to write output to file')
    uniform_group = uniform_parser.add_argument_group(title = 'array parameters')
    uniform_group.add_argument("-N", type = int, help = 'number of elements', default = 4)
    uniform_group.add_argument("-A", type = float, help = 'amplitude of elements',
                       metavar = ('amp',), dest = 'amplitude', default = 1)
    uniform_group.add_argument("-d", type = float, help = 'spacing relative to wavelength',
                       metavar = ('sep',), dest = 'spacing', default = 0.5)
    uniform_group.add_argument("-b", type = float, help = 'phase term [deg]',
                       metavar = ('beta',), dest = 'beta', default = 0)

    # Binomial parser
    bi_description = \
"""Define a nonuniform linear antenna array with binomial excitation coefficients.
"""

    bi_parser = subparsers.add_parser('binomial', help = 'define a nonuniform binomial array',
                                      description = bi_description,
                                      formatter_class = argparse.RawDescriptionHelpFormatter)
    bi_parser.add_argument("--no-plots", action = 'store_true', help = 'flag to skip plots')
    bi_parser.add_argument("--file", action = 'store_true', help = 'flag to write output to file')
    bi_group = bi_parser.add_argument_group(title = 'array parameters')
    bi_group.add_argument("-N", type = int, help = 'number of elements', default = 4)
    bi_group.add_argument("-A", type = float, help = 'max amplitude of elements',
                          metavar = ('amp',), dest = 'amplitude', default = 1)
    bi_group.add_argument("-d", type = float, help = 'spacing relative to wavelength',
                          metavar = ('sep',), dest = 'spacing', default = 0.5)

    # Chebyshev parser
    cheb_description = \
"""Define a Dolph-Tschebyscheff antenna array.
"""

    cheb_parser = subparsers.add_parser('chebyshev', help = 'define a nonuniform chebyshev array',
                                        description = cheb_description,
                                        formatter_class = argparse.RawDescriptionHelpFormatter)
    cheb_parser.add_argument("--no-plots", action = 'store_true', help = 'flag to skip plots')
    cheb_parser.add_argument("--file", action = 'store_true', help = 'flag to write output to file')
    cheb_parser.add_argument("--diff", action = 'store_true', help = 'make a difference pattern')
    cheb_group = cheb_parser.add_argument_group(title = 'array parameters')
    cheb_group.add_argument("-N", type = int, help = 'number of elements', default = 4)
    cheb_group.add_argument("-A", type = float, help = 'max amplitude of elements',
                            metavar = ('amp',), dest = 'amplitude', default = 1)
    cheb_group.add_argument("-d", type = float, help = 'spacing relative to wavelength',
                          metavar = ('sep',), dest = 'spacing', default = 0.5)
    cheb_group.add_argument("-R", type = int, help = 'major / minor lobe ratio [dB]',
                            metavar = ('ratio',), default = 25)

    # Parse command line arguments
    args = parser.parse_args()

    # Print help message and exit program if no parameters given
    if len(sys.argv) == 1:
        parser.print_help(sys.stdout)
        sys.exit(1)
    elif len(sys.argv) == 2:
        cmd = sys.argv[1]
        if cmd == 'uniform':
            uniform_parser.print_help(sys.stdout)
            sys.exit(1)
        elif cmd == 'binomial':
            bi_parser.print_help(sys.stdout)
            sys.exit(1)
        elif cmd == 'chebyshev':
            cheb_parser.print_help(sys.stdout)
            sys.exit(1)

    # Select appropriate class of array
    if args.arrtype == 'uniform':
        array = UniformArray(amplitude = args.amplitude, beta = args.beta,
                             spacing = args.spacing, N = args.N)
    elif args.arrtype == 'binomial':
        array = BinomialArray(amplitude = args.amplitude, spacing = args.spacing, N = args.N)
    elif args.arrtype == 'chebyshev':
        if args.diff:
            array = ChebyshevArray.DifferencePattern(amplitude = args.amplitude, spacing = args.spacing,
                                      N = args.N, R = args.R)
        else:
            array = ChebyshevArray(amplitude = args.amplitude, spacing = args.spacing,
                                   N = args.N, R = args.R)

    # Create chart comparing array specs from program and formula from book
    if args.arrtype == 'uniform':
        book_directivity = approx_uniform_directivity(N = args.N, d = args.spacing)
        book_hpbw = approx_uniform_hpbw(N = args.N, d = args.spacing)
    elif args.arrtype == 'binomial':
        book_directivity = approx_binomial_directivity(N = args.N)
        book_hpbw = approx_binomial_hpbw(N = args.N)
    elif args.arrtype == 'chebyshev':
        book_directivity = approx_chebyshev_directivity(R = args.R, N = args.N, d = args.spacing)
        book_hpbw = approx_chebyshev_hpbw(R = args.R, N = args.N, d = args.spacing)

    array_directivity = round(array.directivity, 2)
    array_hpbw = tuple(array.hpbw_in_degs.round(2))
    chart = pd.DataFrame(data = [[array_directivity, array_hpbw],
                                 [book_directivity, book_hpbw]],
                         index = ['prog', 'book'], columns = ['directivity', 'hpbw'])

    # Print relevant characteristics and comparisons to the console
    print("-----Antenna Array Parameters-----")
    print("Signature: {}".format(repr(array)))
    print("Directivity: {:.2f}".format(array.directivity))
    print("HPBW [deg]: {}".format(tuple(array.hpbw_in_degs.round(2))))
    print()
    print("-----Sidelobe Data-----")
    print(array.side_lobes)
    print()
    print("-----Comparison Chart-----")
    print(chart)

    # Write output to file if file flag set
    if args.file: 
        with open('output.txt', 'w') as f:
            f.write("Command: {}\n\n".format(' '.join(sys.argv)))
            f.write("-----Antenna Array Parameters-----\n")
            f.write("Signature: {}\n".format(repr(array)))
            f.write("Directivity: {:.2f}\n".format(array.directivity))
            f.write("HPBW [deg]: {}\n\n".format(array.hpbw_in_degs))
            f.write("-----Sidelobe Data-----\n")
            f.write(array.side_lobes.to_string() + "\n\n")
            f.write("------Comparison Chart-----\n")
            f.write(chart.to_string() + "\n")
        print("Data written to output.txt")

    # Make plots if no-plots flag not set
    if not args.no_plots:
        array.make_plot(num = 1, pattern = array.intensity_in_db, title = 'Array Pattern (dB)')
        array.make_polar_plot(num = 2, th = array.radians360, af = array.af360_real, title = 'Array Pattern (linear)')
        array.make_3d_plot(num = 3, rho = array.af_real, title = 'Array Pattern (linear)')
        
        if args.arrtype == 'binomial' or args.arrtype == 'chebyshev':
            array.plot_excitations(num = 4, coefs = array.coefs, title = 'Excitation Coefficients')
        
        plt.show()

if __name__ == '__main__':
    main()
