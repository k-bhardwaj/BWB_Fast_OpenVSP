#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    FAST - Copyright (c) 2016 ONERA ISAE
"""

import os

import numpy
import scipy


class CerasEngine(object): ## The Ceras Engine model basically interpolates tabulated values of thrust for different atmospheric conditions.
    """
    #=================================================================================
    #   Model of the CERAS SR Aircraft
    #   The reference tables provided by CERAS provide:
    #   -Thurst in [kN]
    #   -Fuel consumption in kg/s
    #
    #   INPUTS
    #
    #
    #   OUTPUTS
    #   -Thrust [N] for a given throttle setting, Mach and Altitude [ft]
    #   -SFC [Kg/N/s] for a given throttle setting, Mach and Altitude [ft]
    #   -SFC [Kg/N/s] for a given thrust level [N], Mach and Altitude [ft] (Cruise phase)
    #=================================================================================
    """

    def __init__(self):
        # Load engine data
        resource_dir = os.path.join(os.path.dirname(__file__), 'resources')
        file_eng_thrust = open(os.path.join(resource_dir, 'CERAS_Engine_thrust.txt'), 'rb')
        data_eng_thrust = numpy.loadtxt(file_eng_thrust, delimiter=';')

        file_eng_ff = open(os.path.join(resource_dir, 'CERAS_Engine_FF.txt'), 'rb')
        data_eng_ff = numpy.loadtxt(file_eng_ff, delimiter=';')

        mach_ref = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                    0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]

        alt_ref = [0, 3.28084 * 500, 3.28084 * 1000, 3.28084 * 1500, 3.28084 * 2000,
                   3.28084 * 2500, 3.28084 * 3000, 3.28084 * 3500,
                   3.28084 * 4000, 3.28084 * 4500, 3.28084 * 5000, 3.28084 *
                   5500, 3.28084 * 6000, 3.28084 * 6500, 3.28084 * 7000,
                   3.28084 * 7500, 3.28084 * 8000, 3.28084 * 8500, 3.28084 *
                   9000, 3.28084 * 9500, 3.28084 * 10000, 3.28084 * 10500,
                   3.28084 * 11000, 3.28084 * 11500, 3.28084 *
                   12000, 3.28084 * 12500, 3.28084 * 13000, 3.28084 * 13500,
                   3.28084 * 14000]

        self.thrust_rate_ref = [1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55]

        data_eng_thrust = [row for row in data_eng_thrust]
        data_eng_ff = [row2 for row2 in data_eng_ff]
        self.interp_engine_thrust = []
        self.interp_engine_ff = []
        i = 0
        while True:
            self.interp_engine_thrust.append(
                scipy.interpolate.interp2d(mach_ref, alt_ref, data_eng_thrust[i:i + 29]))
            self.interp_engine_ff.append(
                scipy.interpolate.interp2d(mach_ref, alt_ref, data_eng_ff[i:i + 29]))
            i += 29
            if i >= 29 * 12:
                break

    def compute_manual(self, mach, altitude, thrust_rate, phase='MTO'):
        interp_thrust = []
        interp_ff = []
        i = 0
        while True:
            interp_thrust.append(self.interp_engine_thrust[i](mach, altitude)[0])
            interp_ff.append(self.interp_engine_ff[i](mach, altitude)[0])
            i += 1
            if i >= 12:
                break

        thrust_tck = scipy.interpolate.interp1d(self.thrust_rate_ref, interp_thrust)
        ff_tck = scipy.interpolate.interp1d(self.thrust_rate_ref, interp_ff)

        if thrust_rate >= 0.55:
            thrust_interp = thrust_tck(thrust_rate)
            ff_interp = ff_tck(thrust_rate) / (thrust_interp * 1000)
        else:
            thrust_interp = thrust_rate * thrust_tck(1.0)
            ff_interp = ff_tck(0.56) / (thrust_tck(0.56) * 1000)

        thrust_interp = thrust_interp * 1000.
        
        ff_interp=ff_interp*1.0

        return thrust_interp, ff_interp

    def compute_regulated(self, mach, altitude, drag, phase='CRZ'):
        interp_thrust = []
        interp_ff = []
        i = 0
        while True:
            interp_thrust.append(self.interp_engine_thrust[i](mach, altitude)[0])
            interp_ff.append(self.interp_engine_ff[i](mach, altitude)[0])
            i += 1
            if i >= 12:
                break

        tr_tck = scipy.interpolate.interp1d(interp_thrust, self.thrust_rate_ref)
        ff_tck = scipy.interpolate.interp1d(self.thrust_rate_ref, interp_ff)

        tr_interp = tr_tck(drag / 1000.)
        ff_interp = ff_tck(tr_interp) / (drag)
        
        ff_interp=ff_interp*1.0

        return ff_interp, tr_interp
