import mne
import autoreject as ar
import pandas as pd
import collections


def final_reject_epoch(user_params_dict, epochs, raw):
    """Final and automatic rejection of bad epochs
    Parameters
    ----------
    user_params_dict : python dictionary
        user defined variables like tmin and tmax,
    epochs: mne.Epochs object
        instance of the mne.Epochs,
    raw: mne.io.Raw object
        data as mne Raw object

    Returns 
    ----------
    output_dict_finalRej: dictionary
        dictionary with epochs droped per channel and channels interpolated
    """
    
    #creates the output dictionary to store the function output
    output_dict_finalRej = collections.defaultdict(dict)
    output_dict_finalRej['interpolatedChannels']=[]

    #fit epoch data using autoreject
    autoRej = ar.AutoReject()
    autoRej.fit(epochs)

    #Create a rejection log 
    reject_log = autoRej.get_reject_log(epochs)
    #Create a dataframe with the labels that indicate if a channel was interpolated
    df = pd.DataFrame(data=reject_log.labels,columns=raw.info.ch_names)
    for ch in raw.info.ch_names:
        if df[df[ch]==2][ch].count()>0:
            output_dict_finalRej['interpolatedChannels'].append(ch)

    # Get rejection dictionary to reject automatically detected bad epochs
    reject = ar.get_rejection_threshold(epochs)  
    
    for ch in raw.info.ch_names:
        rej_epochs = mne.Epochs(raw, epochs.events, event_id=epochs.event_id, tmin=user_params_dict['tmin'], tmax=user_params_dict['tmax'], #tmin=-0.2 tmax=0.5
                            picks=ch, preload=True, reject=reject, reject_by_annotation=True)
        
        # store amount of epochs dropped for each channel
        output_dict_finalRej['epochsDropped'][ch]=str(rej_epochs.drop_log.count((ch,)))
    return output_dict_finalRej
