"""Verificações numéricas do bootstrap max-t com índices controlados."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import avaliar_contrastes_viagem as module


class MaxTTests(unittest.TestCase):
    def setUp(self):
        self.data = np.array([[1., 2., 4., 7.], [-2., 1., 3., 8.], [0., 2., 5., 6.]])
        self.indices = np.array([[0, 1, 1, 3], [1, 2, 2, 3], [0, 0, 2, 3]])

    def test_matches_independent_scalar_calculation(self):
        import statistics
        result, _, zeros = module.max_statistics(self.data, self.data.mean(axis=1), self.indices)
        expected = []
        for indices in self.indices:
            statistics_for_draw = []
            for row in self.data:
                selected = [float(row[i]) for i in indices]
                se = statistics.stdev(selected)/len(selected)**.5
                statistics_for_draw.append(abs((statistics.mean(selected)-statistics.mean(row))/se))
            expected.append(max(statistics_for_draw))
        np.testing.assert_allclose(result, expected, atol=1e-13)
        self.assertEqual(zeros, 0)

    def test_invariant_to_units_and_common_location_shifts(self):
        original, _, _ = module.max_statistics(self.data, self.data.mean(axis=1), self.indices)
        converted = self.data*np.array([[100.], [.2], [7.]])+np.array([[13.], [4.], [21.]])
        actual, _, _ = module.max_statistics(converted, converted.mean(axis=1), self.indices)
        np.testing.assert_allclose(actual, original, atol=1e-12)

    def test_perfectly_correlated_duplicates_preserve_the_same_maximum(self):
        first = self.data[:1]
        original, _, _ = module.max_statistics(first, first.mean(axis=1), self.indices)
        dependent = np.concatenate([first, 3*first, -2*first], axis=0)
        actual, _, _ = module.max_statistics(dependent, dependent.mean(axis=1), self.indices)
        np.testing.assert_allclose(actual, original, atol=1e-13)

    def test_zero_standard_error_is_retained_as_infinite(self):
        maxima, _, zeros = module.max_statistics(self.data, self.data.mean(axis=1), np.array([[1, 1, 1, 1]]))
        self.assertEqual(zeros, 3)
        self.assertTrue(np.isinf(maxima[0]))

    def test_random_sequence_is_stable_across_batch_sizes(self):
        one = module.bootstrap_max_t(self.data, 123, resamples=1000, batch=37)
        two = module.bootstrap_max_t(self.data, 123, resamples=1000, batch=101)
        np.testing.assert_array_equal(one[0], two[0])
        self.assertEqual(one[2], two[2])


if __name__ == '__main__':
    unittest.main()
