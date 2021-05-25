import autoreject as ar
import pandas as pd
import collections


def final_reject_epoch(epochs):
    """Final and automatic rejection of bad epochs
    Parameters
    ----------
    epochs: mne.Epochs object
            instance of the mne.Epochs,

    Returns
    ----------
    epochs_clean:   mne.Epochs object
                    instance of "cleaned" epochs using autoreject

    output_dict_finalRej:   dictionary
                            dictionary with epochs droped per channel and
                            channels interpolated
    """

    # creates the output dictionary to store the function output
    output_dict_finalRej = collections.defaultdict(dict)
    output_dict_finalRej['interpolatedChannels'] = []

    # fit and clean epoch data using autoreject
    autoRej = ar.AutoReject()
    autoRej.fit(epochs)
    epochs_clean = autoRej.transform(epochs)

    # Create a rejection log
    reject_log = autoRej.get_reject_log(epochs)

    # get channel names
    ch_names = epochs.info.ch_names

    # Create dataframe with the labels of which channel was interpolated
    df = pd.DataFrame(data=reject_log.labels, columns=ch_names)
    for ch in ch_names:
        if df[df[ch] == 2][ch].count() > 0:
            output_dict_finalRej['interpolatedChannels'].append(ch)

    for ch in ch_names:
        # store amount of epochs dropped for each channel
        output_dict_finalRej['epochsDropped'][ch] = str(
            epochs_clean.drop_log.count((ch,)))

    return epochs_clean, output_dict_finalRej
