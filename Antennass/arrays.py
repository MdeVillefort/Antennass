#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linear array classes and functions
ECE 584 Antenna Theory and Design
Midterm Project
@author: Ethan Ross
"""

import numpy as np
import pandas as pd
from scipy.integrate import simps, trapz
from scipy.signal import find_peaks, peak_widths
from scipy.special import binom
from scipy.signal import chebwin
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

class Array:
    """Base array class for defining uniformly spaced antenna linear arrays with
    uniform or nonuniform amplitudes and phases."""
    
    def __init__(self, num_theta = 300, side_lobe_level = 30):
        """Constructor"""
        
        # Define array of polar angles and side lobe level threshold
        self.side_lobe_level = self.from_db(-side_lobe_level)
        self.num_theta = num_theta                              # Note that as N grows large
        self.radians = np.linspace(0, np.pi, self.num_theta)    # angles need to be more finely sampled since patterns
        self.degrees = np.degrees(self.radians)                 # usually contain many more high freq. side lobes
        
        
        # Stuff for the polar plot
        degrees360 = np.linspace(0, 360, 2 * self.num_theta)
        self.radians360 = np.radians(degrees360)

    def __repr__(self):
        """Representation of object for interactive sessions and print()"""
        
        return f"{self.__class__.__name__}(num_theta = {self.num_theta})"
    
    def get_specs(self):
        """Get specs of the antenna array."""
        
        delta = self.radians360[1] -self.radians360[0]
        self.directivity = self.get_directivity(self.radians, self.intensity)
        self.hpbw_in_radians = self.get_hpbw(self.radians360, self.intensity360, delta)
        self.hpbw_in_degs = np.degrees(self.hpbw_in_radians)
        self.side_lobes = pd.DataFrame(self.get_side_lobes(self.radians, self.intensity, self.side_lobe_level),
                                       columns = ['angle', 'value', 'rel_height'])
    
    def get_directivity(self, th, U, rule = 'simps'):
        """Function to compute the maximum directivity given the intensity pattern (th, U).
        The integration is done using Simpson's Rule or the Trapezoidal Rule via the scipy.integrate
        package's simps and trapz functions.
        
        Parameters:
            th = polar angle array
            U = pattern array
            rule = numerical method of integration; 'simps' or 'trapz' else returns None
        Returns:
            directivity = max directivity of the pattern
        """
        
        pi = np.pi
        U_max = np.max(U)
        if rule == 'simps':
            P = 2 * pi * simps(U * np.sin(th), th)
        elif rule == 'trapz':
            P = 2 * pi * trapz(U * np.sin(th), th)
        else:
            print("Rule must be 'simps' or 'trapz'")
            return
        directivity = 4 * pi * U_max / P
        
        return directivity
    
    def get_hpbw(self, th, U, delta, threshold = 0.95):
        """Function to compute the half-power beamwidth of the arrays power pattern.
        The function will calcualte a beamwidth for any peak greater than threshold.
        Returns:
            hpbw = beamwidth(s) in radians
        """
        
        peak_indices, _ = find_peaks(U, height = threshold)
        peak_hp_widths, _, _, _ = peak_widths(U, peak_indices, rel_height = 0.5)
        peak_hp_widths = peak_hp_widths.round(2)
        peak_hp_widths = np.unique(peak_hp_widths)
        peak_hp_widths = peak_hp_widths[peak_hp_widths != 0]
        hpbw = peak_hp_widths * delta
        
        return hpbw
    
    def from_db(self, U):
        """Function to convert from decibel units to dimensionless"""
    
        return 10**(U / 10.0)
    
    def to_db(self, U):
        """Function to convert dimensionless to decibel units"""
    
        return 10 * np.log10(np.abs(U))
    
    def normalize(self, U):
        """Function which will normalize an array to a max value of 1."""
        
        U_max = np.max(U)
        return U / U_max
    
    def get_side_lobes(self, th, U, side_lobe_level):
        """Function to find and return the angle, value, and relative height to max
        of the sidelobe peaks in intensity pattern.  Makes use of scipy.signal package's
        find_peaks function.  
    
        Parameters:
            th = polar angle
            U = intensity pattern
            side_lobe_level = value the peak must equal or exceed to be returned
        Returns:
            lobes = list of lists of angle, value, relative height
        """
        
        buffer = side_lobe_level / 10
        peak_indices, _ = find_peaks(U, height = side_lobe_level - buffer)
        peak_values = U[peak_indices]
        peak_angles = th[peak_indices]
        main_lobe_value = max(peak_values)
        peak_rel_heights = peak_values / main_lobe_value
        
        lobes = []
        for i in range(len(peak_indices)):
            peak_angle = np.degrees(peak_angles[i])
            peak_value = peak_values[i]
            peak_rel_height = peak_rel_heights[i]
            lobes.append([peak_angle, peak_value, peak_rel_height])
            
        return lobes
    
    def make_plot(self, num, pattern, title):
        """Create cartesian plot of array pattern vs polar angle."""
        
        fig = plt.figure(num = num)
        ax = fig.add_subplot(111)
        ax.plot(self.degrees, pattern)
        ax.set_xlabel(r"$\theta$"); ax.set_ylabel('power')
        ax.set_title(title)
        ax.grid(True)
        bottom = -40 if pattern.min() < -40 else pattern.min()
        ax.set_ylim(bottom = bottom, top = 1)
        
        return fig, ax
    
    def make_polar_plot(self, num, th, af, title):
        """Create a polar plot of the array pattern."""
    
        theta_grid_labels = ['0', '30', '60', '90', '120', '150', '180',
                     '150', '120', '90', '60', '30']
        theta_grid_labels = tuple(label + "$^{\circ}$" for label in theta_grid_labels)
        fig_polar = plt.figure(num = num)
        ax_polar = fig_polar.add_subplot(111, projection = 'polar')
        ax_polar.plot(th, np.abs(af))
        ax_polar.set_thetagrids(angles = tuple(range(0, 360, 30)),
                           labels = theta_grid_labels)
        ax_polar.set_theta_zero_location('N')
        ax_polar.set_rlabel_position(-45)
        ax_polar.set_title('Array Factor (linear)')
        ax_polar.grid(True)
        
        return fig_polar, ax_polar
    
    def make_3d_plot(self, num, rho, title):
        """Create a 3d plot of the array pattern.
        rho = absolute value of the array factor."""
        
        fig3d = plt.figure(num = num)
        ax3d = fig3d.add_subplot(111, projection = '3d')
        
        # make data
        u = np.linspace(0, 3 / 2 * np.pi, int(3 / 2 * self.num_theta))
        v = np.linspace(0, np.pi, self.num_theta)
        x = np.outer(np.cos(u), rho * np.sin(v))
        y = np.outer(np.sin(u), rho * np.sin(v))
        z = np.outer(np.ones(np.size(u)), rho * np.cos(v))
        
        # make plot
        ax3d.plot_surface(x, y, z, color = 'y')
        ax3d.set_title(title)
        ax3d.set_xlabel("x"); ax3d.set_ylabel("y")
        ax3d.set_zlabel('power')
        buffer = z.std()
        ax3d.set_zlim(z.min() - 2*buffer, z.max() + 2*buffer)
        
        return fig3d, ax3d

class UniformArray(Array):
    """Uniform array class"""
    
    def __init__(self, amplitude, beta, spacing, N, side_lobe_level = 30, srctype = 'isotropic'):
        super().__init__(side_lobe_level = side_lobe_level)
        
        # Basic parameters
        self.srctype = srctype
        self.amplitude = amplitude
        self.beta = beta # in degrees
        self.spacing = spacing # Must be relative to wavelength, e.g. (1/2) * lambda
        self.N = N
        
        # Calculate array factor
        get_af_func = self.get_af
        self.af, self.af_real, self.af_in_db, \
        self.intensity, self.intensity_in_db, \
        self.af360, self.af360_real, self.intensity360 \
            = self.get_pattern(get_af_func, self.beta, self.spacing)
        
        # Compute directivity, HPBW, and sidelobe levels
        self.get_specs()
    
    def __repr__(self):
        """Representation for interactive sessions and print()"""
        
        return f"{self.__class__.__name__}" \
            + f"(amplitude = {self.amplitude}, " \
            + f"beta = {self.beta}, " \
            + f"spacing = {self.spacing}, " \
            + f"N = {self.N}, " \
            + f"srctype = {self.srctype})"
    
    def phase(self, th, beta, d):
        """Returns phase at particular value of theta in radians.
        phase = kd cos(th) + beta."""
        
        phase = 2 * np.pi * d * np.cos(th) + np.radians(beta)
        return phase
    
    def get_af(self, th, beta, d):
        """Calculate the array factor at angle theta [rad]"""
        
        af = 0
        for n in range(1, self.N + 1):
            af_n = np.exp(1j * (n - 1) * self.phase(th, beta, d))
            af += af_n
        return af
    
    def get_pattern(self, get_af_func, beta, d):
        """Calculate the array's power pattern."""
        
        af = np.array([get_af_func(th, beta, d) for th in self.radians])
        af_real = self.normalize(np.abs(af))
        af_in_db = self.to_db(af_real)
        intensity = af_real**2 # The pattern intensity is the square of the array pattern; see p. 314 of book
        intensity_in_db = self.to_db(intensity)
        af360 = np.array([get_af_func(th, beta, d) for th in self.radians360])
        af360_real = self.normalize(np.abs(af360))
        intensity360 = af360_real**2
        
        return af, af_real, af_in_db, intensity, intensity_in_db, af360, af360_real, intensity360

class NonUniformArray(Array):
    """Nonuniform antenna array class"""
    
    def __init__(self, side_lobe_level = 30):
        super().__init__(side_lobe_level = side_lobe_level)
        
    def __repr__(self):
        return f"{self.__class__.__name__}(num_theta = {self.num_theta})"
    
    def get_af(self, th, coefs, N, M, d, u = lambda x, d: np.pi * d * np.cos(x)):
        """Calculate the array factor at angle theta [rad]"""
        
        af = []
        if N % 2 == 0: # if is even
            for n in range(1, M + 1):
                af_n = np.exp(1j * (2 * n - 1) * u(th, d))
                af.append(af_n)
        else: # if is odd
            for n in range(1, (M + 1) + 1):
                af_n = np.exp(1j * 2 * (n - 1) * u(th, d))
                af.append(af_n)
        af = coefs * np.array(af)
        af = af.sum()
        
        return af
    
    def get_pattern(self, get_af_func, coefs, d, N, M, diff = False):
        """Calculate the pattern in linear and dB scales."""
        
        af = np.array([get_af_func(th, coefs, N, M, d) for th in self.radians])
        
        if diff:
            af_real = self.normalize(af.imag)
        else:
            af_real = self.normalize(af.real)
            
        af_in_db = self.to_db(af_real)
        intensity = af_real**2 # The pattern intensity is the square of the array pattern; see p. 314 of book
        intensity_in_db = self.to_db(intensity)
        af360 = np.array([get_af_func(th, coefs, N, M, d) for th in self.radians360])
        
        if diff:
            af360_real = self.normalize(af360.imag)
        else:
            af360_real = self.normalize(af360.real)
            
        intensity360 = af360_real**2
        
        return af, af_real, af_in_db, intensity, intensity_in_db, af360, af360_real, intensity360
    
    def plot_excitations(self, num, coefs, title):
        """Plot the excitation coefficients of the array."""
        
        fig = plt.figure(num = num)
        ax = fig.add_subplot(111)
        ax.scatter(range(1, len(coefs) + 1), coefs, c = 'r')
        ax.plot(range(1, len(coefs) + 1), coefs, c = 'r')
        ax.set_title(title)
        ax.set_ylabel(r'$a_n$'); ax.set_xlabel('n')
        ax.grid(True)
        
        return fig, ax

class ChebyshevArray(NonUniformArray):
    """Nonuniform amplitude Dolph-Tschebyscheff antenna array class"""
    
    def __init__(self, amplitude, spacing, N , R, diff = False, srctype = 'isotropic'):
        super().__init__(side_lobe_level = R)
        
        # Basic parameters
        self.amplitude = amplitude
        self.spacing = spacing
        self.N = N
        if self.N % 2 == 0:
            self.M = int(self.N / 2)
        else:
            self.M = int((self.N - 1) / 2)
        self.R = R
        self.diff = diff
        self.srctype = srctype
        
        # Calculate array factor
        get_af_func = self.get_diff_af if self.diff else self.get_af
        self.coefs = self.get_excitation_coefs(self.N, self.R)
        self.af, self.af_real, self.af_in_db, \
        self.intensity, self.intensity_in_db, \
        self.af360, self.af360_real, self.intensity360 \
            = self.get_pattern(get_af_func, self.coefs, self.spacing, self.N, self.M, self.diff)
            
        # Compute directivity, HPBW, and sidelobe levels
        self.get_specs()
    
    def __repr__(self):
        """Representation for interactive sessions and print()."""
        
        return f"{self.__class__.__name__}" \
            + f"(amplitude = {self.amplitude}, " \
            + f"spacing = {self.spacing}, " \
            + f"N = {self.N}, " \
            + f"R = {self.R}, " \
            + f"diff = {self.diff}, " \
            + f"srctype = {self.srctype})"
    
    def get_excitation_coefs(self, N , R):
        """Calculate and return the excitation coefficients for the array.
        Parameters:
            N = number of elements
            R = major-minor side lobe ratio [dB]
        """
        
        coefs = chebwin(N, R)
        
        if N % 2 == 0: # if is even
            coefs = np.split(coefs, 2)[-1]
        else: # if is odd
            upto = int((N + 1) / 2)
            coefs = coefs[: upto]
            coefs = np.flip(coefs)
            coefs[0] = coefs[0] / 2
        
        return coefs
    
    def get_diff_af(self, th, coefs, N, M, d, u = lambda x, d: np.pi * d * np.cos(x)):
        """Calculate the array factor at angle theta [rad].  A simple modification
        to NonUniformArray's get_af method where the sign of each term is flipped.
        """
        
        af = []
        if N % 2 == 0: # if is even
            for n in range(1, M + 1):
                af_n = np.exp(1j * (2 * n - 1) * u(th, d))
                af.append(af_n)
            af = np.array(af)
            first, second = np.split(af, 2)
            second *= -1
            af = np.concatenate((first, second))
        else: # if is odd
            for n in range(1, (M + 1) + 1):
                af_n = np.exp(1j * 2 * (n - 1) * u(th, d))
                af.append(af_n)
            af = np.array(af)
            split_point = (len(af) - 1) // 2 + 1
            first = af[:split_point]
            second = af[split_point:]
            second *= -1
            af = np.concatenate((first, second))
        af = coefs * af
        af = af.sum()
        
        return af
    
    @classmethod
    def DifferencePattern(cls, amplitude, spacing, N , R, diff = True, srctype = 'isotropic'):
        """A convenient factory function for creating a Chebyshev differnce pattern"""
        
        array = cls(amplitude, spacing, N , R, diff, srctype)
        return array

class BinomialArray(NonUniformArray):
    """Nonuniform amplitude binomial antenna array class"""
    
    def __init__(self, amplitude, spacing, N, side_lobe_level = 30, srctype = 'isotropic'):
        super().__init__(side_lobe_level = side_lobe_level)
        
        # Basic parameters
        self.amplitude = amplitude
        self.spacing = spacing
        self.N = N
        if self.N % 2 == 0:
            self.M = int(self.N / 2)
        else:
            self.M = int((self.N - 1) / 2)
        self.srctype = srctype
        
        # Calculate array factor
        self.coefs = self.get_excitation_coefs(self.N)
        get_af_func = self.get_af
        self.af, self.af_real, self.af_in_db, \
        self.intensity, self.intensity_in_db, \
        self.af360, self.af360_real, self.intensity360 \
            = self.get_pattern(get_af_func, self.coefs, self.spacing, self.N, self.M)
        
        # Compute directivity, HPBW, and sidelobe levels
        self.get_specs()
    
    def __repr__(self):
        """Representation for interactive sessions and print()"""
        
        return f"{self.__class__.__name__}" \
            + f"(amplitude = {self.amplitude}, " \
            + f"spacing = {self.spacing}, " \
            + f"N = {self.N}, " \
            + f"srctype = {self.srctype})"
    
    def get_excitation_coefs(self, N):
        """Return array of excitation coefficients."""
        
        coefs = binom(N - 1, range(N))
        
        if N % 2 == 0: # if is even
            coefs = np.split(coefs, 2)[-1]
        else: # if is odd
            upto = int((N + 1) / 2)
            coefs = coefs[: upto]
            coefs = np.flip(coefs)
            coefs[0] = coefs[0] / 2
        
        return coefs

# Some functions for validating my code based on equations from the book
def approx_uniform_directivity(N, d):
    """Computes an approximation for directivity for a large, linear, uniform array.
    Uses Eqn. 6.42 from the book.
    Parameters:
        N = number of elements
        d = distance relative to wavelength
    """
    
    D = round(2 * N * d, 2)
    return D

def approx_uniform_hpbw(N, d):
    """Computes an approximation of the HPBW for a large, linear, uniform array.
    Uses formula from Table 6.2 from the book.
    Parameters:
        N = number of elements
        d = distance relative to wavelength
    """
    
    hpbw = 2 * (np.pi / 2 - np.arccos(1.391 / (np.pi * N * d)))
    return round(np.degrees(hpbw), 2)

def approx_binomial_directivity(N):
    """Computes an approximation for directivity for a nonuniform binomial array
    with d = 0.5 * wavelength.  Uses Eqn. 6.65b from the book.
    Parameters:
        N = number of elements
    """
    D = 1.77 * np.sqrt(N)
    return round(D, 2)

def approx_binomial_hpbw(N):
    """Computes an approximation for the HPBW for a nonuniform binomial array
    with d = 0.5 * wavelength.  Uses Eqn. 6.64 from the book.
    Parameters:
        N = number of elements
    """
    
    hpbw = 1.06 / np.sqrt(N - 1)
    return round(np.degrees(hpbw), 2)

def chebyshev_beam_broadening_factor(R):
    """Implementation of Eqn. 6.78 from book.  The beam broadening factor can be
    used to calculate approximations for directivity and HPBW of Chebyshev arrays.
    Parameters:
        R = major / minor lobe ratio [dB]
    """
    
    # Convert to linear scale ratio
    R0 = 10**(R / 20)
    
    f = 1 + 0.636 * (2 / R0 * np.cosh(np.sqrt(np.arccosh(R0)**2 - np.pi**2)))**2
    return f

def approx_chebyshev_directivity(R, N, d):
    """Computes an approximation of directivity for a nonuniform Chebyshev array.
    Parameters:
        R = major / minor lobe ratio [dB]
        N = number of elements
        d = spacing relative to wavelength
    """
    
    # Convert to linear scale ratio and get beam broadening factor
    R0 = 10**(R / 20)
    f = chebyshev_beam_broadening_factor(R)
    
    D = 2 * R0**2 / (1 + (R0**2 - 1) * f / (N * d))
    return round(D, 2)

def approx_chebyshev_hpbw(R, N, d):
    """Computes an approximation of HPBW for a nonuniform Chebyshev array.
    Parameters:
        R = major / minor lobe ratio [dB]
        N = number of elements
        d = spacing relative to wavelength
    """
    
    # Convert to linear scale ratio and get beam broadening factor
    f = chebyshev_beam_broadening_factor(R)
    
    # Get approximate uniform hpbw from Eqn. 6.22a from book
    th0 = np.pi / 2 # for broadside array
    hpbw = np.arccos(np.cos(th0) - 0.443 / (N * d)) \
        - np.arccos(np.cos(th0) + 0.443 / (N * d))
    hpbw = f * hpbw
    
    return round(np.degrees(hpbw), 2)