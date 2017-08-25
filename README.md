# Numerai Python API
Automatically download and upload data for the Numerai machine learning 
competition.

This library is a Python client to the Numerai API. The interface is programmed 
in Python and allows downloading the training data, uploading predictions, and 
accessing user and submission information. Some parts of the code were taken 
from [numerflow](https://github.com/ChristianSch/numerflow) by ChristianSch.  
Visit his 
[wiki](https://github.com/ChristianSch/numerflow/wiki/API-Reverse-Engineering), 
if you need further information on the reverse engineering process.

If you encounter a problem or have suggestions, feel free to open an issue.

# Installation
1. Obtain a copy of this API
  * If you do not plan on contributing to this repository, download a release.
    1. Navigate to [releases](https://github.com/numerai/NumerAPI/releases).
    2. Download the latest version.
    3. Extract with `unzip` or `tar` as necessary.
    
  * If you do plan on contributing, clone this repository instead.

2. `cd` into the API directory (defaults to `numerapi`, but make sure not to go 
into the sub-directory also named `numerapi`).
3. `pip install -e .`

# Usage
See `example.py`.  You can run it as `./example.py`

# Documentation
## Layout
Parameters and return values are given with Python types. Dictionary keys are 
given in quotes; other names to the left of colons are for reference 
convenience only. In particular, `list`s of `dict`s have names for the `dict`s; 
these names will not show up in the actual data, only the actual `dict` data 
itself.

## `login`
### Parameters
* `email` (`str`, optional): email of user account
  * will prompt for this value if not supplied
* `password` (`str`, optional): password of user account
  * will prompt for this value if not supplied
  * prompting is recommended for security reasons
* `prompt_for_mfa` (`bool`, optional): indication of whether to prompt for MFA 
  code
  * only necessary if MFA is enabled for user account
### Return Values
* `user_credentials` (`dict`): credentials for logged-in user
  * `"username"` (`str`)
  * `"access_token"` (`str`)
  * `"refresh_token"` (`str`)

## `download_current_dataset`
### Parameters
* `dest_path` (`str`, optional, default: `.`): destination folder for the 
  dataset
* `unzip` (`bool`, optional, default: `True`): indication of whether the 
  training data should be unzipped
### Return Values
* `success` (`bool`): indication of whether the current dataset was 
  successfully downloaded

## `get_all_competitions`
### Return Values
* `all_competitions` (`list`): information about all competitions
  * `competition` (`dict`)
    * `"_id"` (`int`)
        * `"dataset_id"` (`str`)
        * `"start_date"` (`str (datetime)`)
        * `"end_date"` (`str (datetime)`)
        * `"paid"` (`bool`)
        * `"leaderboard`" (`list`)
          * `submission` (`dict`)
            * `"concordant"` (`dict`)
              * `"pending"` (`bool`)
              * `"value"` (`bool`)
            * `"earnings"` (`dict`)
              * `"career"` (`dict`)
                * `"nmr"` (`str`)
                * `"usd"` (`str`)
              * `"competition"` (`dict`)
                * `"nmr"` (`str`)
                * `"usd"` (`str`)
            * `"logloss"` (`dict`)
              * `"consistency"` (`int`)
              * `"validation"` (`float`)
            * `"original"` (`dict`)
              * `"pending"` (`bool`)
              * `"value"` (`bool`)
            * `"submission_id"` (`str`)
            * `"username"` (`str`)

## `get_competition`
### Return Values
* `competition` (`dict`): information about requested competition
  * `_id` (`int`)
    * `"dataset_id"` (`str`)
    * `"start_date"` (`str (datetime)`)
    * `"end_date"` (`str (datetime)`)
    * `"paid"` (`bool`)
    * `"leaderboard"` (`list`)
      * `submission` (`dict`)
        * `"concordant"` (`dict`)
          * `"pending"` (`bool`)
          * `"value"` (`bool`)
        * `"earnings"` (`dict`)
          * `"career"` (`dict`)
            * `"nmr"` (`str`)
            * `"usd"` (`str`)
          * `"competition"` (`dict`)
            * `"nmr"` (`str`)
            * `"usd"` (`str`)
        * `"logloss"` (`dict`)
          `"consistency"`: (int`)
          `"validation"`: (float`)
        * `"original"` (`dict`)
          * `"pending"` (`bool`)
          * `"value"` (`bool`)
        * `"submission_id"` (`str`)
        * `"username"` (`str`)

## `get_earnings_per_round`
### Parameters
* `username`: user for which earnings are requested
### Return Values
* `round_ids` (`np.ndarray(int)`): IDs of each round for which there are 
  earnings
* `earnings` (`np.ndarray(float)`): earnings for each round

## `get_scores_for_user`
### Parameters
* `username`: user for which scores are being requested
### Return Values
* `validation_scores` (`np.ndarray(float)`): logloss validation scores
* `consistency_scoress` (`np.ndarray(float)`): logloss consistency scores
* `round_ids` (`np.ndarray(int`): IDs of the rounds for which there are scores

## `get_user`
### Parameters
* `username`: `str` - name of requested user
### Return Values
* `user` (`dict`): information about the requested user
  * `"_id"` (`str`)
  * `"username"` (`str`)
  * `"assignedEthAddress"` (`str`)
  * `"created"` (`str (datetime)`)
  * `"earnings"` (`float`)
  * `"followers"` (`int`)
  * `"rewards"` (`list`)
    * `reward` (`dict`)
      * `"_id"` (`int`)
      * `"amount"` (`float`)
      * `"earned"` (`float`)
      * `"nmr_earned"` (`str`)
      * `"start_date"` (`str (datetime)`)
      * `"end_date"` (`str (datetime)`)
  * `"submissions"` (`dict`)
    * `"results"` (`list`)
      * `result` (`dict`)
        * `"_id"` (`str`)
        * `"competition"` (`dict`)
          * `"_id"` (`str`)
          * `"start_date"` (`str (datetime)`)
          * `"end_date"` (`str (datetime)`)
        * `"competition_id"` (`int`)
        * `"created"` (`str (datetime)`)
        * `"id"` (`str`)
        * `"username"` (`str`)

## `get_submission_for_round`
### Parameters
* `username` (`str`): user for which submission is requested
* `round_id` (`int`, optional): round for which submission is requested
  * if no `round_id` is supplied, the submission for the current round will be 
    retrieved
### Return Values
* `username` (`str`): user for which submission is requested
* `submission_id` (`str`): ID of submission for which data was found
* `logloss_val` (`float`): amount of logloss for given submission
* `logloss_consistency` (`float`): consistency of given submission
* `career_usd` (`float`): amount of USD earned by given user
* `career_nmr` (`float`): amount of NMR earned by given user
* `concordant` (`bool` OR `dict` (see note)): whether given submission is 
  concordant
  * for rounds before 64, this was only a boolean, but from 64 on, it is a dict
    which indicates whether concordance is still being computed
* `original` (`bool` OR `dict` (see note)): whether given submission is 
  original
  * for rounds before 64, this was only a boolean, but from 64 on, it is a dict
    which indicates whether originality is still being computed

## `upload_predictions`
### Parameters
* `file_path` (`str`): path to CSV of predictions
  * should already contain the file name (e.g. `"path/to/file/prediction.csv"`)

### Return Values
* `success`: indicator of whether the upload succeeded

### Notes
* Uploading a prediction shortly before a new dataset is released may result in 
  a `400 Bad Request`. If this happens, wait for the new dataset and attempt to 
  upload again.
* Uploading too many predictions in a certain amount of time will result in a 
  `429 Too Many Requests`.
