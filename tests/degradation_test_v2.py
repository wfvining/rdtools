""" Degradation Module Tests. """

import unittest
import sys

import pandas as pd
import numpy as np

from rdtools import degradation_ols, degradation_classical_decomposition, degradation_year_on_year


class DegradationTestCase(unittest.TestCase):
    ''' Unit tests for degradation module.
        Works with both python and nosetests
    '''

    def get_corr_energy(self, rd, input_freq):
        ''' Create input for degradation_ols function, depending on frequency.
            Allowed frequencies for this degradation function are 'MS', 'M', 'W', 'D'
            'H', 'T' and 'S'.
        '''
        if (input_freq == 'MS'):
            x = pd.date_range(start='2012-01-01', end='2015-01-01', freq=input_freq)
            N = len(x)
            months = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / 12, months)
            corr_energy = pd.Series(data=y, index=x)
        elif (input_freq == 'M'):
            x = pd.date_range(start='2012-01-31', end='2015-01-31', freq=input_freq)
            N = len(x)
            months = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / 12, months)
            corr_energy = pd.Series(data=y, index=x)
        elif (input_freq == 'W'):
            x = pd.date_range(start='2012-01-01', end='2015-01-01', freq=input_freq)
            N = len(x)
            weeks = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / 52, weeks)
            corr_energy = pd.Series(data=y, index=x)
        elif (input_freq == 'D'):
            x = pd.date_range(start='2012-01-01', end='2015-01-01', freq=input_freq)
            N = len(x)
            days = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / 365, days)
            corr_energy = pd.Series(data=y, index=x)
        elif (input_freq == 'H'):
            x = pd.date_range(start='2012-01-01 00:00:00', end='2015-01-02 00:00:00', freq=input_freq)
            N = len(x)
            hours = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / (365 * 24), hours)
            corr_energy = pd.Series(data=y, index=x)
        elif (input_freq == 'T'):
            x = pd.date_range(start='2012-01-01 00:00:00', end='2015-01-01 00:50:00', freq=input_freq)
            N = len(x)
            minutes = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / (365 * 24 * 60), minutes)
            corr_energy = pd.Series(data=y, index=x)
        elif (input_freq == 'S'):
            x = pd.date_range(start='2012-01-01 00:00:00', end='2015-01-01 00:10:00', freq=input_freq)
            N = len(x)
            seconds = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / (365 * 24 * 60 * 60), seconds)
            corr_energy = pd.Series(data=y, index=x)
        elif (input_freq == 'Irregular_D'):
            x = pd.date_range(start='2012-01-01', end='2015-01-01', freq='D')
            N = len(x)
            days = np.arange(N)
            y = np.ones(N) * np.power(1 + rd / 365, days)
            corr_energy = pd.DataFrame(y, index=x)
            corr_energy = corr_energy.sample(frac=0.8)
            corr_energy = corr_energy[0]
        else:
            sys.exit("Unknown frequency type")

        return corr_energy

    def setUp(self):
        # define module constants and parameters

        # All frequencies
        self.list_all_input_freq = ['MS', 'M', 'W', 'D', 'H', 'T', 'S', 'Irregular_D']

        # Allowed frequencies for degradation_ols
        self.list_ols_input_freq = ['MS', 'M', 'W', 'D', 'H', 'T', 'S', 'Irregular_D']

        # Allowed frequencies for ddegradation_classical_decomposition
        # in principle CD works on higher frequency data but that makes the
        # tests painfully slow
        self.list_CD_input_freq = ['MS', 'M', 'W', 'D']

        # Allowed frequencies for degradation_year_on_year
        self.list_YOY_input_freq = ['MS', 'M', 'W', 'D', 'Irregular_D']

        self.rd = -0.005

        test_corr_energy = {}

        for input_freq in self.list_all_input_freq:
            corr_energy = self.get_corr_energy(self.rd, input_freq)
            test_corr_energy[input_freq] = corr_energy

        self.test_corr_energy = test_corr_energy

        # for input_freq in self.list_ols_input_freq:
        #     corr_energy = self.get_ols_corr_energy(self.rd, input_freq)
        #     test_ols_corr_energy[input_freq] = corr_energy

        # self.test_ols_corr_energy = test_ols_corr_energy

        # for input_freq in self.list_CD_YOY_input_freq:
        #     corr_energy = self.get_CD_YOY_corr_energy(self.rd, input_freq)
        #     test_CD_YOY_corr_energy[input_freq] = corr_energy

        # self.test_CD_YOY_corr_energy = test_CD_YOY_corr_energy

    def tearDown(self):
        pass

    def test_degradation_with_ols(self):
        ''' Test degradation with ols. '''

        funcName = sys._getframe().f_code.co_name
        print '\r', 'Running ', funcName

        # test ols degradation calc
        for input_freq in self.list_ols_input_freq:
            print 'Frequency: ', input_freq
            rd_result = degradation_ols(self.test_corr_energy[input_freq])
            self.assertAlmostEqual(rd_result[0], 100 * self.rd, places=1)
            print 'Actual: ', 100 * self.rd
            print 'Estimated: ', rd_result[0]

        # TODO
        # - support for different time series frequencies
        # - inputs

    def test_degradation_classical_decomposition(self):
        ''' Test degradation with classical decomposition. '''

        funcName = sys._getframe().f_code.co_name
        print '\r', 'Running ', funcName

        # test classical decomposition degradation calc
        for input_freq in self.list_CD_input_freq:
            print 'Frequency: ', input_freq
            rd_result = degradation_classical_decomposition(self.test_corr_energy[input_freq])
            self.assertAlmostEqual(rd_result[0], 100 * self.rd, places=1)
            print 'Actual: ', 100 * self.rd
            print 'Estimated: ', rd_result[0]
        # TODO
        # - support for different time series frequencies
        # - inputs

    def test_degradation_year_on_year(self):
        ''' Test degradation with year on year approach. '''

        funcName = sys._getframe().f_code.co_name
        print '\r', 'Running ', funcName

        # test YOY degradation calc
        for input_freq in self.list_YOY_input_freq:
            print 'Frequency: ', input_freq
            rd_result = degradation_year_on_year(self.test_corr_energy[input_freq])
            self.assertAlmostEqual(rd_result[0], 100 * self.rd, places=1)
            print 'Actual: ', 100 * self.rd
            print 'Estimated: ', rd_result[0]

        # TODO
        # - support for different time series frequencies
        # - inputs


if __name__ == '__main__':
    unittest.main()
