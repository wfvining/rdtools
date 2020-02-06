""" Filtering Module Tests. """

import unittest

import pandas as pd
import numpy as np

from rdtools import csi_filter, poa_filter, tcell_filter, clip_filter, \
    stale_values_filter, interpolation_filter, irradiance_limits_filter


ALBUQUERQUE = {'latitude': 35.05, 'longitude': -106.5, 'altitude': 1619}


class CSIFilterTestCase(unittest.TestCase):
    ''' Unit tests for clear sky index filter.'''

    def setUp(self):
        self.measured_poa = np.array([1, 1, 0, 1.15, 0.85])
        self.clearsky_poa = np.array([1, 2, 1, 1.00, 1.00])

    def test_csi_filter(self):
        filtered = csi_filter(self.measured_poa,
                              self.clearsky_poa,
                              threshold=0.15)

        # Expect clearsky index is filtered with threshold of +/- 0.15.
        expected_result = np.array([True, False, False, True, True])
        self.assertListEqual(filtered.tolist(), expected_result.tolist())


class POAFilterTestCase(unittest.TestCase):
    ''' Unit tests for plane of array insolation filter.'''

    def setUp(self):
        self.measured_poa = np.array([201, 1199, 500, 200, 1200])

    def test_poa_filter(self):
        filtered = poa_filter(self.measured_poa,
                              low_irradiance_cutoff=200,
                              high_irradiance_cutoff=1200)

        # Expect high and low POA cutoffs to be non-inclusive.
        expected_result = np.array([True, True, True, False, False])
        self.assertListEqual(filtered.tolist(), expected_result.tolist())


class TcellFilterTestCase(unittest.TestCase):
    ''' Unit tests for cell temperature filter.'''

    def setUp(self):
        self.tcell = np.array([-50, -49, 0, 109, 110])

    def test_tcell_filter(self):
        filtered = tcell_filter(self.tcell,
                                low_tcell_cutoff=-50,
                                high_tcell_cutoff=110)

        # Expected high and low tcell cutoffs to be non-inclusive.
        expected_result = np.array([False, True, True, True, False])
        self.assertListEqual(filtered.tolist(), expected_result.tolist())


class ClipFilterTestCase(unittest.TestCase):
    ''' Unit tests for inverter clipping filter.'''

    def setUp(self):
        self.power = pd.Series(np.arange(1, 101))
        # Note: Power is expected to be Series object because clip_filter makes
        #       use of the Series.quantile() method.

    def test_clip_filter_upper(self):
        filtered = clip_filter(self.power, quant=0.98,
                               low_power_cutoff=0)

        # Expect 99% of the 98th quantile to be filtered
        expected_result = self.power < (98 * 0.99)
        self.assertTrue((expected_result == filtered).all())

    def test_clip_filter_low_cutoff(self):
        filtered = clip_filter(self.power, quant=0.98,
                               low_power_cutoff=2)

        # Expect power <=2 to be filtered
        expected_result = (self.power > 2)
        self.assertTrue((expected_result.iloc[0:5] == filtered.iloc[0:5]).all())


class StaleValueFilterTestCase(unittest.TestCase):
    ''' Unit tests for stale value filter.'''

    def setUp(self):
        self.data = pd.Series(
            [1.0, 1.001, 1.001, 1.001, 1.001,
             1.001001, 1.001, 1.001, 1.2, 1.3])
        self.data_with_negatives = pd.Series(
            [0.0, 0.0, 0.0, -0.0, 0.00001, 0.000010001, -0.00000001])

    def test_stale_value_defaults(self):
        filtered = stale_values_filter(self.data)
        self.assertListEqual(filtered.tolist(),
                             [False, False, False, True, True,
                              True, True, True, False, False])

    def test_low_tolerance_small_window(self):
        filtered = stale_values_filter(self.data, rtol=1e-8, window=2)
        self.assertListEqual(filtered.tolist(),
                             [False, False, True, True, True,
                              False, False, True, False, False])

    def test_large_window(self):
        filtered7 = stale_values_filter(self.data, window=7)
        filtered8 = stale_values_filter(self.data, window=8)
        self.assertListEqual(filtered7.tolist(),
                             [False, False, False, False, False,
                              False, False, True, False, False])
        self.assertFalse(all(filtered8))

    def test_negative_values(self):
        filtered = stale_values_filter(self.data_with_negatives)
        self.assertListEqual(filtered.tolist(),
                             [False, False, True, True,
                              False, False, False])

        filtered = stale_values_filter(self.data_with_negatives,
                                       atol=1e-3)
        self.assertListEqual(filtered.tolist(),
                             [False, False, True, True,
                              True, True, True])
        filtered = stale_values_filter(self.data_with_negatives, atol=1e-5)
        self.assertListEqual(filtered.tolist(),
                             [False, False, True, True,
                              True, False, False])
        filtered = stale_values_filter(self.data_with_negatives, atol=2e-5)
        self.assertListEqual(filtered.tolist(),
                             [False, False, True, True,
                              True, True, True])

    def test_bad_window_raises_exception(self):
        with self.assertRaises(ValueError):
            stale_values_filter(self.data, window=1)


class InterpolationFilterTestCase(unittest.TestCase):
    ''' Unit tests for interpolation filter.'''

    def setUp(self):
        self.data = pd.Series(
            [1.0, 1.001, 1.002001, 1.003, 1.004, 1.001001, 1.001001,
              1.001001, 1.2, 1.3, 1.5, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0])

        self.data_with_negatives = pd.Series(
            [0.0, 0.0, 0.0, -0.0, 0.00001, 0.000010001, -0.00000001])

    def test_default_parameters(self):
        self.assertListEqual(
            interpolation_filter(self.data).tolist(),
            [False, False, False, False, False,
             False, False, True, False, False,
             False, False, False, True, True, True,
             False])

    def test_tolerance(self):
        filtered = interpolation_filter(self.data, rtol=1e-2)
        self.assertListEqual(
            filtered.tolist(),
            [False, False, True, True, True,
             False, False, True, False, False,
             False, False, False, True, True, True,
             False])

        filtered = interpolation_filter(self.data, atol=1e-2)
        self.assertListEqual(
            filtered.tolist(),
            [False, False, True, True, True,
             True, True, True, False, False,
             False, False, False, True, True, True,
             False])

    def test_larger_window(self):
        filtered = interpolation_filter(self.data, window=5)
        self.assertListEqual(
            filtered.tolist(),
            [False, False, False, False, False,
             False, False, False, False, False,
             False, False, False, False, False,
             True, False])

    def test_negative_values(self):
        filtered = interpolation_filter(self.data_with_negatives, atol=1e-5)
        self.assertListEqual(
            filtered.tolist(),
            [False, False, True, True, True, True, False])

    def test_bad_window_raises_exception(self):
        with self.assertRaises(ValueError):
            interpolation_filter(self.data, window=2)


class IrradianceLimitsFilterTestCase(unittest.TestCase):
    ''' Unit tests for irradiance_limits_filter'''

    def setUp(self):
        self.location = ALBUQUERQUE
        self.data = pd.Series([-100, 100, 100, 1000, 1000, 1000, 1000,
                               1000, 1000, 500, 1000, 500, 500, 0])
        self.data.index = pd.date_range(start='01-01-2020 09:30:00',
                                        freq='15T', periods=14)
        self.data.tz_localize('America/Denver')

    def test_no_data_returns_all_none(self):
        x, y, z = irradiance_limits_filter(**self.location)
        self.assertIsNone(x)
        self.assertIsNone(y)
        self.assertIsNone(z)

    def test_passing_ghi_returns_ghi_mask(self):
        ghi, dhi, dni = irradiance_limits_filter(**self.location, ghi=self.data)
        self.assertIsNotNone(ghi)
        self.assertIsNone(dhi)
        self.assertIsNone(dni)

    def test_passing_dhi_returns_dhi_mask(self):
        ghi, dhi, dni = irradiance_limits_filter(**self.location, dhi=self.data)
        self.assertIsNone(ghi)
        self.assertIsNotNone(dhi)
        self.assertIsNone(dni)

    def test_passing_dni_returns_dni_mask(self):
        ghi, dhi, dni = irradiance_limits_filter(**self.location, dni=self.data)
        self.assertIsNone(ghi)
        self.assertIsNone(dhi)
        self.assertIsNotNone(dni)


if __name__ == '__main__':
    unittest.main()
