# -*- coding: utf-8 -*-

# System
import zipfile
import json
import os
from datetime import datetime, timedelta
import getpass
import errno
import logging

# Third Party
import requests
import numpy as np


class NumerAPI(object):

    """Wrapper around the Numerai API"""

    def __init__(self, verbosity="INFO"):
        """
        initialize Numerai API wrapper for Python

        verbosity: indicates what level of messages should be displayed
            valid values: "debug", "info", "warning", "error", "critical"
        """
        self.logger = logging.getLogger(__name__)

        # set up logging
        numeric_log_level = getattr(logging, verbosity.upper())
        if not isinstance(numeric_log_level, int):
            raise ValueError('invalid verbosity: %s' % verbosity)
        log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        self._date_format = "%Y-%m-%dT%H:%M:%S"
        logging.basicConfig(format=log_format, level=numeric_log_level,
                            datefmt=self._date_format)

        # Numerai API base URL
        self.api_base_url = "https://api.numer.ai"

        # first round to check for scores
        self._FIRST_ROUND = 51

        # error indicating user is not logged in
        not_logged_in_msg = "username not specified and not logged in"
        self._not_logged_in_error = ValueError(not_logged_in_msg)
        self._username = None
        self._access_token = None
        self.url_paths = None

    def __get_url(self, url_path_name, query_params=None):
        """get url with query params for Numerai API"""

        # mappings of URL path names to URL paths
        self.url_paths = {
            "login": "/sessions",
            "auth": "/submission_authorizations",
            "dataset": "/competitions/current/dataset",
            "submissions": "/submissions",
            "users": "/users",
            "competitions": "/competitions",
            "competitions_by_id": "/competitions/id",
            "current_leaderboard_url": "/currentLeaderboard"
        }

        # set query params based on type
        if query_params is None:
            query_params_str = ""
        elif isinstance(query_params, dict):
            query_params_str = "?" + json.dumps(query_params)
        elif isinstance(query_params, str):
            query_params_str = "?" + query_params
        else:
            self.logger.warning("invalid query params")
            query_params = ""

        return (self.api_base_url +
                self.url_paths[url_path_name] +
                query_params_str)

    def __get_username(self, username):
        """set username if logged in and not specified"""
        if username is None:
            if hasattr(self, "_username"):
                username = self._username
            else:
                raise self._not_Logged_in_error

        return username

    def __unzip_file(self, src_path, dest_path, filename):
        """unzips file located at src_path into destination_path"""
        self.logger.info("unzipping file...")

        # construct full path (including file name) for unzipping
        unzip_path = "{0}/{1}".format(dest_path, filename)

        # create parent directory for unzipped data
        try:
            os.makedirs(unzip_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # extract data
        with zipfile.ZipFile(src_path, "r") as z:
            z.extractall(unzip_path)

        return True

    def __authorize_file_upload(self, file_path):
        """authorize file upload"""
        self.logger.info("authorizing file upload...")

        # user must be logged in in order to upload files
        if not hasattr(self, "_access_token"):
            self.logger.error("you must log in first")
            self.login()

        # set up request parameters
        auth_headers = {
            "Authorization": "Bearer {0}".format(self._access_token)
        }
        auth_url = self.__get_url("auth")
        auth_data = {
            "filename": file_path.split("/")[-1],
            "mimetype": "text/csv"
        }

        # send auth request
        auth_res = requests.post(auth_url, data=auth_data,
                                 headers=auth_headers)
        auth_res.raise_for_status()

        # parse auth response
        auth_res_dict = auth_res.json()
        filename = auth_res_dict["filename"]
        signed_req = auth_res_dict["signedRequest"]

        return (filename, signed_req, auth_headers)

    def login(self, email=None, password=None, mfa_enabled=False):
        """log user in and store credentials"""
        self.logger.info("logging in...")

        # get login parameters if necessary
        if email is None:
            email = input("email: ")
        if password is None:
            password = getpass.getpass("password: ")
        mfa_code = None
        if mfa_enabled:
            mfa_code = getpass.getpass("MFA code: ")

        # send login request
        post_data = {"email": email, "password": password, "code": mfa_code}
        login_url = self.__get_url("login")
        login_res = requests.post(login_url, data=post_data)
        login_res.raise_for_status()

        # parse login response
        user = login_res.json()
        access_token = user["accessToken"]
        username = user["username"]

        # set instance variables
        self._access_token = access_token
        self._username = username

        # set up return object
        whitelisted_keys = ["username", "accessToken", "refreshToken"]
        user_credentials = {key: user[key] for key in whitelisted_keys}

        return user_credentials

    def download_current_dataset(self, dest_path=".", unzip=True):
        """download dataset for current round

        dest_path: desired location of dataset file
        unzip: indicates whether to unzip dataset
        """
        self.logger.info("downloading current dataset...")

        # set up download path
        now = datetime.now().strftime("%Y%m%d")
        dataset_name = "numerai_dataset_{0}".format(now)
        file_name = "{0}.zip".format(dataset_name)
        dataset_path = "{0}/{1}".format(dest_path, file_name)

        # get data for current dataset
        dataset_res = requests.get(self.__get_url("dataset"), stream=True)
        dataset_res.raise_for_status()

        # create parent folder if necessary
        try:
            os.makedirs(dest_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # write dataset to file
        with open(dataset_path, "wb") as f:
            for chunk in dataset_res.iter_content(1024):
                f.write(chunk)

        # unzip dataset
        if unzip:
            self.__unzip_file(dataset_path, dest_path, dataset_name)

        return True

    def get_all_competitions(self):
        """get all competitions from first round stored in instance variable"""
        self.logger.info("getting all competitions...")

        # get latest round to determine end of round ID range
        current_round = self.get_competition()
        last_round_id = current_round["_id"]

        # store data from all competitions
        all_competitions = []
        for i in range(self._FIRST_ROUND, last_round_id):
            all_competitions.append(self.get_competition(round_id=i))
        all_competitions.append(current_round)

        return all_competitions

    def get_competition(self, round_id=None):
        """get a specific competiton, defaults to most recent"""
        self.logger.info("getting competition...")

        # set up request URL
        # defaults to getting most recent round
        if round_id is None:
            # indicates that the API returns an array and should be parsed
            # accordingly
            returns_array = True

            # set up JSON query
            now = datetime.now()
            tdelta = timedelta(microseconds=55296e5)
            current_date = now - tdelta
            current_date_str = current_date.strftime(self._date_format)
            jsonq = {
                "end_date": {
                    "$gt": current_date_str
                }
            }

            comp_req_url = self.__get_url("competitions", query_params=jsonq)

        # otherwise set up the request with the specified round ID
        else:
            returns_array = False
            jsonq = {"id": str(round_id)}
            comp_req_url = self.__get_url("competitions_by_id", query_params=jsonq)

        # send compititon request
        comp_res = requests.get(comp_req_url)
        comp_res.raise_for_status()

        # parse competition response
        competition = comp_res.json()
        if returns_array:
            competition = competition[0]

        return competition

    def get_earnings_per_round(self, username=None):
        """get earnings for every round"""
        self.logger.info("getting earnings...")

        # construct user request URL
        username = self.__get_username(username)
        user_req_url = "{0}/{1}".format(self.__get_url("users"), username)

        # send user request
        user_res = requests.get(user_req_url)
        user_res.raise_for_status()

        # parse response
        user = user_res.json()
        rewards = user["rewards"]
        num_rewards = len(rewards)
        round_ids = np.zeros(num_rewards, dtype="int")
        earnings = np.zeros(num_rewards)
        for i in range(num_rewards):
            round_ids[i] = rewards[i]["_id"]
            earnings[i] = rewards[i]["amount"]

        return (round_ids, earnings)

    def get_scores_for_user(self, username=None):
        """get scores for specified user"""
        self.logger.info("getting scores for user...")

        # get all competitions
        competitions = self.get_all_competitions()

        # set up variables to parse and store scores
        username = self.__get_username(username)
        num_competitions = len(competitions)
        validation_scores = []
        consistency_scores = []
        round_ids = []

        # loop over compitions to append scores
        for i in range(num_competitions):
            # get submissions for user for round i
            competition = competitions[i]
            leaderboard = competition["leaderboard"]
            submissions = list(filter(lambda s: s["username"] == username,
                                      leaderboard))

            # append scores if any exist for round i
            if submissions:
                logloss = submissions[0]["logloss"]
                validation_scores.append(logloss["validation"])
                consistency_scores.append(logloss["consistency"])
                round_ids.append(competition["_id"])

        # convert score arrays to numpy arrays
        validation_scores = np.array(validation_scores)
        consistency_scores = np.array(consistency_scores)
        round_ids = np.array(round_ids, dtype="int")

        return (validation_scores, consistency_scores, round_ids)

    def get_user(self, username=None):
        """get user information"""
        self.logger.info("getting user...")

        # construct user request URL
        username = self.__get_username(username)
        user_req_url = self.__get_url("users") + "/" + username

        # send user request
        user_res = requests.get(user_req_url)
        user_res.raise_for_status()

        # parse user response
        user = user_res.json()

        return user

    def get_submission_for_round(self, username=None, round_id=None):
        """gets submission for single round"""
        self.logger.info("getting user submission for round...")

        # get username for filtering competition leaderboard
        username = self.__get_username(username)

        # get competition for specified round
        competition = self.get_competition(round_id=round_id)

        # parse user submission data
        for user in competition["leaderboard"]:
            if user["username"] == username:
                submission_id = user["submission_id"]
                logloss_val = np.float(user["logloss"]["validation"])
                logloss_consistency = np.float(user["logloss"]["consistency"])
                career_usd = np.float(user["earnings"]["career"]["usd"].replace(",", ""))
                career_nmr = np.float(user["earnings"]["career"]["nmr"].replace(",", ""))
                concordant = user["concordant"]
                original = user["original"]

                return (username, submission_id, logloss_val, logloss_consistency,
                        career_usd, career_nmr, concordant, original)

        # return an empty tuple if user is not on the leaderboard
        self.logger.warning("user \"{0}\" is not on leaderboard".format(username))
        return ()

    def upload_predictions(self, file_path):
        """uploads predictions from file"""
        self.logger.info("uploading prediction...")

        # parse information for file upload
        filename, signed_url, headers = self.__authorize_file_upload(file_path)

        # get information for current competition
        competition = self.get_competition()
        dataset_id = competition["dataset_id"]
        competition_id = competition["_id"]

        # open file
        with open(file_path, "rb") as fp:
            # upload file
            file_res = requests.Request("PUT", signed_url, data=fp.read())
            prepared_file_res = file_res.prepare()
            req_session = requests.Session()
            res_prepped = req_session.send(prepared_file_res)
            res_prepped.raise_for_status()

        # get submission URL
        sub_url = self.__get_url("submissions")
        # construct submission data
        sub_data = {
            "competition_id": competition_id,
            "dataset_id": dataset_id,
            "filename": filename
        }

        # send file request
        sub_res = requests.post(sub_url, data=sub_data, headers=headers)
        sub_res.raise_for_status()

        return True
