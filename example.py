#!/usr/bin/env python

from datetime import datetime
import json

from numerapi.numerapi import NumerAPI


def main():
    # set example username and round
    example_username = "xanderai"
    example_round = 51

    # set up paths for download of dataset and upload of predictions
    now = datetime.now().strftime("%Y%m%d")
    dataset_parent_folder = "./dataset"
    dataset_name = "numerai_dataset_{0}/example_predictions.csv".format(now)
    dataset_path = "{0}/{1}".format(dataset_parent_folder, dataset_name)

    # most API calls do not require logging in
    napi = NumerAPI(verbosity="info")

    # log in
    credentials = napi.login()
    print(json.dumps(credentials, indent=2))

    # download current dataset
    dl_succeeded = napi.download_current_dataset(dest_path=dataset_parent_folder,
                                                 unzip=True)
    print("download succeeded: " + str(dl_succeeded))

    # get competitions (returned data is too long to print practically)
    # all_competitions = napi.get_all_competitions()
    # current_competition = napi.get_competition()
    # example_competition = napi.get_competition(round_id=example_round)

    # get user earnings per round
    user_earnings = napi.get_earnings_per_round()
    print("user earnings:")
    print(user_earnings)
    example_earnings = napi.get_earnings_per_round(username=example_username)
    print("example earnings:")
    print(example_earnings)

    # get scores for user
    personal_scores = napi.get_scores_for_user()
    print("personal scores:")
    print(personal_scores)
    other_scores = napi.get_scores_for_user(username=example_username)
    print("other scores:")
    print(other_scores)

    # get user information
    current_user = napi.get_user()
    print("current user:")
    print(json.dumps(current_user, indent=2))
    example_user = napi.get_user(username=example_username)
    print("example user:")
    print(json.dumps(example_user, indent=2))

    # get submission for given round
    submission = napi.get_submission_for_round(username=example_username,
                                               round_id=example_round)
    print("submission:")
    print(json.dumps(submission, indent=2))

    # upload predictions
    ul_succeeded = napi.upload_predictions(dataset_path)
    print("upload succeeded: " + str(ul_succeeded))


if __name__ == "__main__":
    main()
