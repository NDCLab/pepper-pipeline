import numpy as np
from collections import namedtuple


def spearman_brown(correlation_coefficient):
    """Apply Spearman Brown Correction
    Parameters
    ----------

    Returns
    ----------

    """
    return (2 * correlation_coefficient) / (1 + abs(correlation_coefficient))


def split_half(data, number_permutations):
    """Compute split-half reliability for a single measure
    Parameters
    ----------

    Returns
    ----------

    """

    distribution = namedtuple('distribution', ['mean', 'lower', 'upper'])
    split_half_result = namedtuple('split_half_result', ['correlation', 'reliability'])

    rng = np.random.default_rng()

    corr_coefs = np.zeros(number_permutations)
    sb_reliability = np.zeros(number_permutations)

    for n in range(number_permutations):
        data_random_split = [np.array_split(rng.permutation(d), 2) for d in data] # permute each array, split into 2
        mean_by_split = [[np.mean(split) for split in group] for group in data_random_split] # mean of each split
        corr_value = np.corrcoef(np.array(mean_by_split), rowvar=False)[0, 1] # [0,1] to retain 1 value from sym matrix
        corr_coefs[n] = corr_value
        sb_reliability[n] = spearman_brown(corr_value) # Spearman-Brown correction

    correlation_dist = distribution(np.mean(corr_coefs), np.quantile(corr_coefs, .025), np.quantile(corr_coefs, .975))
    reliability_dist = distribution(np.mean(sb_reliability), np.quantile(sb_reliability, .025), np.quantile(sb_reliability, .975))
    return split_half_result(correlation_dist, reliability_dist)
