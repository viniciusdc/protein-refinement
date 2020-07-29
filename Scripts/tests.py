import os
from Matlab.test import sdp_test
from Scripts.spectral_projected_gradient import spg_test


def routine_test():
    # run tests
    spg_test()
    sdp_test()
