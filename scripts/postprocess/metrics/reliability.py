import numpy as np
from collections import namedtuple


def spearman_brown(correlation_coefficient):
    """Apply Spearman-Brown Correction, to convert a Pearson correlation to
    measure of reliability.
    Parameters
    ----------
    correlation_coefficient: float
                             The correlation coefficient to use

    Returns
    ----------
    float
        The measure of reliability
    """
    return (2 * correlation_coefficient) / (1 + abs(correlation_coefficient))


def split_half(data_group_one, data_group_two=None, number_permutations=5000):
    """Compute split-half reliability for either a single measure, or a
    difference between two measures.
    Parameters
    ----------
    data_group_one: list
                    A list of 1D numpy arrays. Each array represents data from
                    one group.

    data_group_two: list, optional
                    A list of 1D numpy arrays. Each array represents data from
                    one group.

    number_permutations: int, optional
                         The number of split half permutations to compute

    Returns
    ----------
    namedtuple
        For both correlation and reliability, the mean, lower, and upper 95%
        CI of the distribution across permutations
    """

    if data_group_two is None:
        compute_difference = False
    else:
        compute_difference = True

    if compute_difference and (len(data_group_one) != len(data_group_two)):
        raise ValueError(
            'When computing a difference, data_group_one and data_group_two \
             must be the same length')

    distribution = namedtuple('distribution', ['mean', 'lower', 'upper'])
    split_half_result = namedtuple(
        'split_half_result', ['correlation', 'reliability'])

    rng = np.random.default_rng()

    corr_coefs = np.zeros(number_permutations)
    sb_reliability = np.zeros(number_permutations)

    for n in range(number_permutations):
        data_random_split = [np.array_split(rng.permutation(
            d), 2) for d in data_group_one]  # permute each array, split
        # mean of each split
        mean_by_split = np.array([[np.mean(split) for split in group]
                                  for group in data_random_split])
        # do the same for the second group of data if computing difference
        if compute_difference:
            data_random_split_two = [np.array_split(
                rng.permutation(d), 2) for d in data_group_two]
            mean_by_split_two = np.array(
                [[np.mean(split) for split in group] for group in
                 data_random_split_two])
            mean_by_split = mean_by_split - mean_by_split_two
        # [0,1] to retain 1 value from sym matrix
        corr_value = np.corrcoef(mean_by_split, rowvar=False)[0, 1]
        corr_coefs[n] = corr_value
        sb_reliability[n] = spearman_brown(
            corr_value)  # Spearman-Brown correction

    correlation_dist = distribution(np.mean(corr_coefs), np.quantile(
        corr_coefs, .025), np.quantile(corr_coefs, .975))
    reliability_dist = distribution(np.mean(sb_reliability), np.quantile(
        sb_reliability, .025), np.quantile(sb_reliability, .975))
    return split_half_result(correlation_dist, reliability_dist)
