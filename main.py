#!/usr/bin/env python3

#
# euserv auto-renew script v2022.03.04
#
# SPDX-FileCopyrightText: (c) 2021-2022 Bitsavers
# SPDX-FileCopyrightText: (c) 2020-2021 CokeMine & its repository contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import os
import re
import json
import time
import base64

from typing import Dict, Tuple
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPDataError

import requests
from pyairtable import Table, Api
from bs4 import BeautifulSoup

# Please use one space to separate multiple accounts
# euserv customer id
CUSTOMERIDS = os.environ["CUSTOMERIDS"]
# euserv password
PASSWORDS = os.environ["PASSWORDS"]

# default value is TrueCaptcha demo credential,
# you can use your own credential via set environment variables:
# TRUECAPTCHA_USERID and TRUECAPTCHA_APIKEY
# demo: https://apitruecaptcha.org/demo
# demo2: https://apitruecaptcha.org/demo2
# demo apikey also has a limit of 100 times per day
# {
# 'error': '101.0 above free usage limit 100 per day and no balance',
# 'requestId': '7690c065-70e0-4757-839b-5fd8381e65c7'
# }
TRUECAPTCHA_USERID = os.environ.get("TRUECAPTCHA_USERID", "arun56")
TRUECAPTCHA_APIKEY = os.environ.get("TRUECAPTCHA_APIKEY", "wMjXmBIcHcdYqO2RrsVN")

# Checking CAPTCHA API usage, options: True or False
CHECK_CAPTCHA_SOLVER_USAGE = True

# options: ZapierAirtable or Mailparser
LOGIN_PIN_SENDER = "ZapierAirtable"
# options: ZapierAirtable or Mailparser
RENEW_PIN_SENDER = "ZapierAirtable"

# For getting login PIN from airtable, zapier send email to airtable
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
# Please use one space to separate multiple airtable base ids,
# in order to correspond to the EUserv customer id.
AIRTABLE_BASE_IDS = os.environ.get("AIRTABLE_BASE_IDS")
AIRTABLE_TABLE_NAME_FOR_LOGIN = "Login"
AIRTABLE_TABLE_NAME_FOR_RENEW = "Renew"

# Extract key data from your emails, automatically. https://mailparser.io
# 30 Emails/Month, 10 inboxes and unlimited downloads for free.
# Please use one space to separate multiple mailparser download link ids,
# in order to correspond to the EUserv customer id.
MAILPARSER_DL_IDS_FOR_LOGIN = os.environ.get("MAILPARSER_DL_IDS_FOR_LOGIN")
MAILPARSER_DL_IDS_FOR_RENEW = os.environ.get("MAILPARSER_DL_IDS_FOR_RENEW")

# Waiting time of receiving login PIN, units are seconds.
WAITING_TIME_OF_LOGIN_PIN = 20
# Waiting time of receiving renew PIN, units are seconds.
WAITING_TIME_OF_RENEW_PIN = 20

# Maximum number of login retry
LOGIN_MAX_RETRY_COUNT = 5

# Telegram Bot Push https://core.telegram.org/bots/api#authorizing-your-bot
# Obtained via @BotFather application, for example: 1077xxx4424:AAFjv0FcqxxxxxxgEMGfi22B4yh15R5uw
TG_BOT_TOKEN = ""
# User, group or channel ID, for example: 129xxx206
TG_USER_ID = ""
# Build your own API reverse proxy address for use when the network environment is inaccessible,
# and keep the default if the network is normal.
TG_API_HOST = "https://api.telegram.org"

# Email notification via yandex service, you can modify yourself to use other email service notifications.
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "")
YD_EMAIL = os.environ.get("YD_EMAIL", "")
# yandex mail using third party APP authorization code
YD_APP_PWD = os.environ.get("YD_APP_PWD", "")

# Server Chan(Server 酱, name in Chinese) https://sct.ftqq.com
# Free quota: up to 5 messages per day, cards show only title, maximum 1000 API requests per day, up to 5 messages per minute.
# Server Chan SENDKEY, no need to push can be ignored
SERVER_CHAN_SENDKEY = os.environ.get("SERVER_CHAN_SENDKEY", "")

# Magic internet access (optinal)
# support http(s) proxy via the below approach, 
# PROXIES = {
#     "http": "http://127.0.0.1:7890", 
#     "https": "http://127.0.0.1:7890"
# }
# response = requests.get(url, proxies=PROXIES)

# if you need socks proxy, via the below approach, 
# pip install requests[socks]
# import requests
# PROXIES = {
#     "http":'socks5://127.0.0.1:7890',
#     "https":'socks5://127.0.0.1:7890'
# }
# response = requests.get(url, proxies=PROXIES)


# Language Options: en/chs/cht, or leave it blank
LOG_LANG = "en"
log_lang_options = dict()
if LOG_LANG not in ["en", "", None]:
    try:
        import locales
        # Localization
        log_lang_options = {
            "en": lambda x: x,
            "chs": lambda x: locales.chs_locale.get(x, x),
            "cht": lambda x: locales.cht_locale.get(x, x),
        }
    except ImportError:
        print("Cannot find locales file. So log will display in English.")


# Blank
desp = ""
ordinal = lambda n: "{}{}".format(
    n,
    "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
)


def log(info: str):
    print(info)
    global desp
    desp = desp + info + "\n\n"


# Telegram Bot Push https://core.telegram.org/bots/api#authorizing-your-bot
def telegram():
    data = (
        ("chat_id", TG_USER_ID),
        (
            "text",
            "{}\n\n".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("EUserv Renewal Logs")
            )
            + desp,
        ),
    )
    response = requests.post(
        TG_API_HOST + "/bot" + TG_BOT_TOKEN + "/sendMessage", data=data
    )
    if response.status_code != 200:
        print(
            "Telegram Bot {}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("push failed")
            )
        )
    else:
        print(
            "Telegram Bot {}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("push successfully")
            )
        )


# Yandex mail notification
def send_mail_by_yandex(
    to_email, from_email, subject, text, files, sender_email, sender_password
):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.attach(MIMEText(text, _charset="utf-8"))
    if files is not None:
        for file in files:
            file_name, file_content = file
            # print(file_name)
            part = MIMEApplication(file_content)
            part.add_header(
                "Content-Disposition", "attachment", filename=("gb18030", "", file_name)
            )
            msg.attach(part)
    s = SMTP_SSL("smtp.yandex.ru", 465)
    s.login(sender_email, sender_password)
    try:
        s.sendmail(msg["From"], msg["To"], msg.as_string())
    except SMTPDataError as e:
        raise e
    finally:
        s.close()


# eMail push
def email():
    msg = (
        "{}\n\n".format(
            log_lang_options.get(LOG_LANG, lambda x: x)("EUserv Renewal Logs")
        )
        + desp
    )
    try:
        send_mail_by_yandex(
            RECEIVER_EMAIL,
            YD_EMAIL,
            log_lang_options.get(LOG_LANG, lambda x: x)("EUserv Renewal Logs"),
            msg,
            None,
            YD_EMAIL,
            YD_APP_PWD,
        )
        print(
            "eMail {}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("push successfully")
            )
        )
    except requests.exceptions.RequestException as e:
        print(str(e))
        print(
            "eMail {}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("push failed")
            )
        )
    except SMTPDataError as e1:
        print(str(e1))
        print(
            "eMail {}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("push failed")
            )
        )


# Server Chan https://sct.ftqq.com
def server_chan():
    data = {
        "title": log_lang_options.get(LOG_LANG, lambda x: x)("EUserv Renewal Logs"),
        "desp": desp,
    }
    response = requests.post(
        f"https://sctapi.ftqq.com/{SERVER_CHAN_SENDKEY}.send", data=data
    )
    if response.status_code != 200:
        print(
            "{} {}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("Server Chan"),
                log_lang_options.get(LOG_LANG, lambda x: x)("push failed"),
            )
        )
    else:
        print(
            "{} {}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("Server Chan"),
                log_lang_options.get(LOG_LANG, lambda x: x)("push successfully"),
            )
        )


class EUserv(object):

    class TrueCaptcha(object):

        def __init__(self, userid: str, apikey: str):
            self.URL = "https://api.apitruecaptcha.org/one"
            self.CAPTCHA_IMAGE_URL = "https://support.euserv.com/securimage_show.php"
            self.userid = userid
            self.apikey = apikey

        def captcha_solver(self, session: requests.session) -> Dict:
            """
            TrueCaptcha API doc: https://apitruecaptcha.org/api
            Free to use 100 requests per day.
            - response::
            {
                "result": "", ==> Or "result": 0
                "conf": 0.85,
                "usage": 0,
                "requestId": "ed0006e5-69f0-4617-b698-97dc054f9022",
                "version": "dev2"
            }
            """
            response = session.get(self.CAPTCHA_IMAGE_URL)
            encoded_string = base64.b64encode(response.content)

            # Since "case": "mixed", "mode": "human"
            # can sometimes cause internal errors in the truecaptcha server.
            # So a more relaxed constraint(lower/upper & default) is used here.
            # Plus, the CAPTCHA of EUserv is currently case-insensitive, so the below adjustment works.
            data = {
                "userid": self.userid,
                "apikey": self.apikey,
                # case sensitivity of text (upper | lower| mixed)
                "case": "lower",
                # use human or AI (human | default)
                "mode": "default",
                "data": str(encoded_string)[2:-1],
            }
            r = requests.post(url=f"{self.URL}/gettext", json=data)
            j = json.loads(r.text)
            return j
        
        def handle_captcha_solved_result(self, solved: Dict) -> str:
            """Since CAPTCHA sometimes appears as a very simple binary arithmetic expression.
            But since recognition sometimes doesn't show the result of the calculation directly,
            that's what this function is for.
            """
            if "result" in solved:
                solved_result = solved["result"]
                if isinstance(solved_result, str):
                    if "RESULT  IS" in solved_result:
                        log(
                            "[Captcha Solver] {}{}".format(
                                log_lang_options.get(LOG_LANG, lambda x: x)(
                                    "You are using the demo apikey"
                                ),
                                log_lang_options.get(LOG_LANG, lambda x: x)("."),
                            )
                        )
                        print(
                            "{}{}".format(
                                log_lang_options.get(LOG_LANG, lambda x: x)(
                                    "There is no guarantee that demo apikey will work in the future"
                                ),
                                log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                            )
                        )
                        # because using demo apikey
                        text = re.findall(r"RESULT  IS . (.*) .", solved_result)[0]
                    else:
                        # using your own apikey
                        log(
                            "[Captcha Solver] {}{}".format(
                                log_lang_options.get(LOG_LANG, lambda x: x)(
                                    "You are using your own apikey"
                                ),
                                log_lang_options.get(LOG_LANG, lambda x: x)("."),
                            )
                        )
                        text = solved_result
                    operators = ["X", "x", "+", "-"]
                    if any(x in text for x in operators):
                        for operator in operators:
                            operator_pos = text.find(operator)
                            if operator == "x" or operator == "X":
                                operator = "*"
                            if operator_pos != -1:
                                left_part = text[:operator_pos]
                                right_part = text[operator_pos + 1 :]
                                if left_part.isdigit() and right_part.isdigit():
                                    return eval(
                                        "{left} {operator} {right}".format(
                                            left=left_part, operator=operator, right=right_part
                                        )
                                    )
                                else:
                                    # Because these symbols("X", "x", "+", "-") do not appear at the same time,
                                    # it just contains an arithmetic symbol.
                                    return text
                    else:
                        return text
                else:
                    print(
                        "[Captcha Solver] {}{} {}".format(
                            log_lang_options.get(LOG_LANG, lambda x: x)("Returned JSON"),
                            log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                            solved,
                        )
                    )
                    log(
                        "[Captcha Solver] {}{}".format(
                            log_lang_options.get(LOG_LANG, lambda x: x)("TrueCaptcha Service Exception"),
                            log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                        )
                    )
                    raise ValueError("[Captcha Solver] TrueCaptcha Service Exception!")
            else:
                print(
                    "[Captcha Solver] {}{} {}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)("Returned JSON"),
                        log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                        solved,
                    )
                )
                log(
                    "[Captcha Solver] {}{}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "Failed to find parsed results"
                        ),
                        log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                    )
                )
                raise KeyError("[Captcha Solver] Failed to find parsed results!")
        
        def get_captcha_solver_usage(self) -> Dict:
            params = {
                "username": self.userid,
                "apikey": self.apikey,
            }
            r = requests.get(url=f"{self.URL}/getusage", params=params)
            j = json.loads(r.text)
            return j
    
    class CaptchaSolver(object):
        """
        Solve Captcha locally instead of TrueCaptcha.
        """
        pass

    class ZapierAirtable(object):

        def __init__(self, api_key: str, base_id: str, table_name: str):
            self.api_key = api_key
            self.base_id = base_id
            self.table_name = table_name
        
        def get_pin(self) -> str:
            """
            - airtable response format:
            {
                "id": "rec1234567890",
                "fields": {
                    "Index": 6, 
                    "PIN": "123456",
                    "Last Modified Time": "2022-03-04T12:30:50.000Z"
                },
                "createdTime": '2022-03-04T12:30:50.000Z'
            }
            """
            table = Table(self.api_key, self.base_id, self.table_name)
            # https://pyairtable.readthedocs.io/en/latest/api.html#pyairtable.api.Table.first
            records = table.first(sort=["-Index"])
            if records:
                return records['fields']['PIN']
            return ""

        def cleanup_all_records(self):
            table = Table(self.api_key, self.base_id, self.table_name)
            api = Api(self.api_key)
            for records in api.iterate(self.base_id, self.table_name, page_size=10, max_records=1200, sort=["Index"]):
                record_ids = [record["id"] for record in records]
                table.batch_delete(record_ids)

    class Mailparser(object):
 
        def __init__(self):
            # mailparser parsed data download base url
            self.MAILPARSER_DL_BASE_URL = "https://files.mailparser.io/d/"
        
        def get_pin(self, url_id: str) -> str:
            """
            mailparser response format:
            [
                {
                    "id": "83b95f50f6202fb03950afbe00975eab",
                    "received_at": "2021-11-06 02:30:07",  ==> up to mailparser account timezone setting, here is UTC 0000.
                    "processed_at": "2021-11-06 02:30:07",
                    "pin": "123456"
                }
            ]
            """
            response = requests.get(
                f"{self.MAILPARSER_DL_BASE_URL}{url_id}",
                # Mailparser parsed data download using Basic Authentication.
                # auth=("<your mailparser username>", "<your mailparser password>")
            )
            res = response.json()
            if res:
                return res[0]["pin"]
            else:
                return ""

    def __init__(self, customer_ids, passwords):
        self.URL = "https://support.euserv.com/index.iphp"
        self.LOGO_PNG_URL = "https://support.euserv.com/pic/logo_small.png"
        self.USER_AGENT = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/99.0.4844.51 Safari/537.36"
        )
        self.customer_ids = customer_ids
        self.passwords = passwords

        # Checking CAPTCHA API usage, options: True or False
        self.check_captcha_solver_usage = CHECK_CAPTCHA_SOLVER_USAGE
        # Waiting time of receiving login PIN, units are seconds.
        self.waiting_time_of_login_pin = WAITING_TIME_OF_LOGIN_PIN
        # Waiting time of receiving renew PIN, units are seconds.
        self.waiting_time_of_renew_pin = WAITING_TIME_OF_RENEW_PIN
        self.truecaptcha_userid = TRUECAPTCHA_USERID
        self.truecaptcha_apikey = TRUECAPTCHA_APIKEY
        # For getting login PIN from airtable, zapier send email to airtable
        self.airtable_api_key = AIRTABLE_API_KEY
        # Please use one space to separate multiple airtable base ids,
        # in order to correspond to the EUserv customer id.
        self.airtable_base_ids = AIRTABLE_BASE_IDS
        self.airtable_table_name_for_login = AIRTABLE_TABLE_NAME_FOR_LOGIN
        self.airtable_table_name_for_renew = AIRTABLE_TABLE_NAME_FOR_RENEW
        self.captcha_solver = self.TrueCaptcha(self.truecaptcha_userid, self.truecaptcha_apikey)
    
    def _login_retry(*args, **kwargs):
        def wrapper(func):
            def inner(self, username, password, pin_sender, pin_sender_id):
                ret, ret_session = func(self, username, password, pin_sender, pin_sender_id)
                max_retry = kwargs.get("max_retry")
                # default retry 3 times
                if not max_retry:
                    max_retry = 3
                number = 0
                if ret == "-1":
                    while number < max_retry:
                        number += 1
                        if number > 1:
                            log(
                                "[EUserv] {} {}".format(
                                    log_lang_options.get(LOG_LANG, lambda x: x)(
                                        "Login retried the @@@ time"
                                    ).replace("@@@", ordinal(number)),
                                    log_lang_options.get(LOG_LANG, lambda x: x)("."),
                                )
                            )
                        sess_id, session = func(self, username, password, pin_sender, pin_sender_id)
                        if sess_id != "-1":
                            return sess_id, session
                        else:
                            if number == max_retry:
                                return sess_id, session
                else:
                    return ret, ret_session
            return inner
        return wrapper

    def finish_login_process_via_captcha_code(self, session: requests.session, sess_id: str) -> Tuple[str, requests.session]:
        # every 24 hours
        headers = {"user-agent": self.USER_AGENT, "origin": "https://www.euserv.com"}
        log(
            "[Captcha Solver] {}{}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)(
                    "Performing CAPTCHA recognition"
                ),
                log_lang_options.get(LOG_LANG, lambda x: x)("..."),
            )
        )
        solved_result = self.captcha_solver.captcha_solver(session)
        try:
            captcha_code = self.captcha_solver.handle_captcha_solved_result(solved_result)
            log(
                "[Captcha Solver] {}{} {}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)(
                        "The recognized CAPTCHA is"
                    ),
                    log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                    captcha_code,
                )
            )
            if self.check_captcha_solver_usage:
                usage = self.captcha_solver.get_captcha_solver_usage()
                log(
                    "[Captcha Solver] {} {} {}{} {}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)("Current date"),
                        usage[0]["date"],
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "TrueCaptcha api usage count"
                        ),
                        log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                        usage[0]["count"],
                    )
                )
            r = session.post(
                self.URL,
                headers=headers,
                data={
                    "subaction": "login",
                    "sess_id": sess_id,
                    "captcha_code": captcha_code,
                },
            )
            r.raise_for_status()
            if (
                r.text.find(
                    "To finish the login process please solve the following captcha."
                )
                == -1
            ):
                log(
                    "[Captcha Solver] {}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "CAPTCHA Verification passed"
                        )
                    )
                )
                return sess_id, session
            else:
                log(
                    "[Captcha Solver] {}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "CAPTCHA Verification failed"
                        )
                    )
                )
                return "-1", session
        except (KeyError, ValueError):
            return "-1", session

    def finish_login_process_via_pin(
        self, 
        customer_id: str,
        session: requests.session, 
        sess_id: str, 
        pin_sender: str,
        pin_sender_id: str
        ) -> Tuple[str, requests.session]:
        # every login try
        url = self.URL
        headers = {"user-agent": self.USER_AGENT, "origin": "https://www.euserv.com"}
        log(
            "[PIN Solver] {}{}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)(
                    f"Getting login PIN from {pin_sender}"
                ),
                log_lang_options.get(LOG_LANG, lambda x: x)("..."),
            )
        )
        time.sleep(self.waiting_time_of_login_pin)
        if pin_sender == "Mailparser": 
            l_pin = self.Mailparser().get_pin(pin_sender_id)
        elif pin_sender == "ZapierAirtable":
            l_pin = self.ZapierAirtable(self.airtable_api_key, pin_sender_id, self.airtable_table_name_for_login).get_pin()
        else:
            l_pin = ""
        if l_pin:
            log(
                "[PIN Solver] {}{} {}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)("PIN"),
                    ":",
                    l_pin
                )
            )
            r = session.post(
                url,
                headers=headers,
                data={
                    "Submit": "Confirm",
                    "subaction": "login",
                    "sess_id": sess_id,
                    "pin": l_pin,
                    "c_id": customer_id
                },
            )
            if (
                r.text.find(
                    "To finish the login process enter the PIN that you receive via email."
                )
                == -1
            ):
                log(
                    "[PIN Solver] {}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "Login PIN Verification passed"
                        )
                    )
                )
                return sess_id, session
            else:
                log(
                    "[PIN Solver] {}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "Login PIN Verification failed"
                        )
                    )
                )
                time.sleep(1)
                return "-1", session
        else:
            time.sleep(1)
            return "-1", session

    @_login_retry(max_retry=LOGIN_MAX_RETRY_COUNT)
    def login(self, customer_id: str, password: str, pin_sender: str, pin_sender_id: str) -> Tuple[str, requests.session]:
        url = self.URL
        headers = {"user-agent": self.USER_AGENT, "origin": "https://www.euserv.com"}
        session = requests.Session()

        sess = session.get(self.URL, headers=headers)
        sess_id = re.findall("PHPSESSID=(\\w{10,100});", str(sess.headers))[0]
        # visit small logo
        session.get(self.LOGO_PNG_URL, headers=headers)

        login_data = {
            "email": customer_id,
            "password": password,
            "form_selected_language": "en",
            "Submit": "Login",
            "subaction": "login",
            "sess_id": sess_id,
        }
        r = session.post(url, headers=headers, data=login_data)
        r.raise_for_status()
        resp_text = r.text

        if (
            resp_text.find("Hello") == -1
            and resp_text.find("Confirm or change your customer data here") == -1
        ):
            if (
                resp_text.find(
                    "To finish the login process please solve the following captcha."
                )
                == -1
            ):
                if (
                    resp_text.find(
                        "To finish the login process enter the PIN that you receive via email."
                    )
                    == -1
                ):
                    return "-1", session
                else:
                    return self.finish_login_process_via_pin(customer_id, session, sess_id, pin_sender, pin_sender_id)
            else:
                s_id, ss = self.finish_login_process_via_captcha_code(session, sess_id)
                if s_id == "-1":
                    return "-1", ss
                else:
                    return self.finish_login_process_via_pin(customer_id, ss, s_id, pin_sender, pin_sender_id)
        else:
            return sess_id, session

    def get_servers(self, sess_id: str, session: requests.session) -> Dict:
        url = f"{self.URL}?sess_id={sess_id}"
        headers = {"user-agent": self.USER_AGENT, "origin": "https://www.euserv.com"}
        d = dict()

        f = session.get(url=url, headers=headers)
        f.raise_for_status()
        soup = BeautifulSoup(f.text, "html.parser")
        for tr in soup.select(
            "#kc2_order_customer_orders_tab_content_1 .kc2_order_table.kc2_content_table tr"
        ):
            server_id = tr.select(".td-z1-sp1-kc")
            if not len(server_id) == 1:
                continue
            flag = (
                True
                if tr.select(".td-z1-sp2-kc .kc2_order_action_container")[0]
                .get_text()
                .find("Contract extension possible from")
                == -1
                else False
            )
            d[server_id[0].get_text()] = flag
        return d

    def renew(
        self,
        sess_id: str,
        session: requests.session,
        password: str,
        order_id: str,
        pin_sender: str,
        pin_sender_id: str,
        ) -> bool:
        """
        - pin_sender:
        "Mailparser" or "ZapierAirtable"
        """
        url = self.URL
        headers = {
            "user-agent": self.USER_AGENT,
            "Host": "support.euserv.com",
            "origin": "https://support.euserv.com",
            "Referer": "https://support.euserv.com/index.iphp",
        }
        data = {
            "Submit": "Extend contract",
            "sess_id": sess_id,
            "ord_no": order_id,
            "subaction": "choose_order",
            "choose_order_subaction": "show_contract_details",
        }
        session.post(url, headers=headers, data=data)

        # pop up 'Security Check' window, it will trigger 'send PIN' automatically.
        session.post(
            url,
            headers=headers,
            data={
                "sess_id": sess_id,
                "subaction": "show_kc2_security_password_dialog",
                "prefix": "kc2_customer_contract_details_extend_contract_",
                "type": "1",
            },
        )

        # # trigger 'Send new PIN to your Email-Address' (optional),
        # new_pin = session.post(url, headers=headers, data={
        #     "sess_id": sess_id,
        #     "subaction": "kc2_security_password_send_pin",
        #     "ident": f"kc2_customer_contract_details_extend_contract_{order_id}"
        # })
        # if not json.loads(new_pin.text)["rc"] == "100":
        #     print("new PIN Not Sended")
        #     return False

        # sleep several seconds waiting for mailparser email parsed PIN
        time.sleep(self.waiting_time_of_renew_pin)
        if pin_sender == "Mailparser":
            # pin_sender_id <==> mailparser_dl_url_id
            pin = self.Mailparser().get_pin(pin_sender_id)
            log(
                "[Mailparser] {}{} {}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)("PIN"),
                    log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                    pin,
                )
            )
        else:
            # pin_sender_id <==> pin_sender_id
            pin = self.ZapierAirtable(self.airtable_api_key, pin_sender_id, self.airtable_table_name_for_renew).get_pin()
            log(
                "[ZapierAirtable] {}{} {}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)("PIN"),
                    log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                    pin,
                )
            )

        # using PIN instead of password to get token
        data = {
            "auth": pin,
            "sess_id": sess_id,
            "subaction": "kc2_security_password_get_token",
            "prefix": "kc2_customer_contract_details_extend_contract_",
            "type": 1,
            "ident": f"kc2_customer_contract_details_extend_contract_{order_id}",
        }
        r = session.post(url, headers=headers, data=data)
        r.raise_for_status()
        resp_text = r.text
        if not json.loads(resp_text)["rs"] == "success":
            return False
        token = json.loads(resp_text)["token"]["value"]
        data = {
            "sess_id": sess_id,
            "ord_id": order_id,
            "subaction": "kc2_customer_contract_details_extend_contract_term",
            "token": token,
        }
        session.post(url, headers=headers, data=data)
        time.sleep(5)
        return True

    def check(self, sess_id: str, session: requests.session):
        print(
            "{}{}".format(
                log_lang_options.get(LOG_LANG, lambda x: x)("Checking"),
                log_lang_options.get(LOG_LANG, lambda x: x)("..."),
            )
        )
        d = self.get_servers(sess_id, session)
        flag = True
        for key, val in d.items():
            if val:
                flag = False
                log(
                    "[EUserv] {}{} {} {}{}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)("ServerID"),
                        log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                        key,
                        log_lang_options.get(LOG_LANG, lambda x: x)("Renew Failed"),
                        log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                    )
                )

        if flag:
            log(
                "[EUserv] {}{} {}{}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)("ALL Work Done"),
                    log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                    log_lang_options.get(LOG_LANG, lambda x: x)("Enjoy"),
                    log_lang_options.get(LOG_LANG, lambda x: x)("~"),
                )
            )

    def compute(self):
        if not self.customer_ids or not self.passwords:
            log(
                "[EUserv] {}{}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)(
                        "You have not added any accounts"
                    ),
                    log_lang_options.get(LOG_LANG, lambda x: x)("."),
                )
            )
            exit(1)
        user_list = self.customer_ids.strip().split()
        passwd_list = self.passwords.strip().split()
        if len(user_list) != len(passwd_list):
            log(
                "[EUserv] {}{}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)(
                        "The number of customerids and passwords do not match"
                    ),
                    log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                )
            )
            exit(1)

        # login_pin_sender = ""
        # renew_pin_sender = ""
        # login_pin_sender_ids = []
        # renew_pin_sender_ids = []
        if LOGIN_PIN_SENDER == "Mailparser" and RENEW_PIN_SENDER == "Mailparser":
            mailparser_dl_ids_for_login = MAILPARSER_DL_IDS_FOR_LOGIN.strip().split()
            mailparser_dl_ids_for_renew = MAILPARSER_DL_IDS_FOR_RENEW.strip().split()
            if len(mailparser_dl_ids_for_login) != len(user_list) or len(mailparser_dl_ids_for_renew) != len(user_list):
                log(
                    "[Mailparser] {}{}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "The number of mailparser_dl_ids_for_login or mailparser_dl_ids_for_renew do not match with customerids"
                        ),
                        log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                    )
                )
                exit(1)
            login_pin_sender = "Mailparser"
            renew_pin_sender = "Mailparser"
            login_pin_sender_ids = mailparser_dl_ids_for_login
            renew_pin_sender_ids = mailparser_dl_ids_for_renew
        elif LOGIN_PIN_SENDER == "Mailparser" and RENEW_PIN_SENDER == "ZapierAirtable":
            mailparser_dl_ids_for_login = MAILPARSER_DL_IDS_FOR_LOGIN.strip().split()
            base_ids = AIRTABLE_BASE_IDS.strip().split()
            if len(mailparser_dl_ids_for_login) != len(user_list) or len(base_ids) != len(user_list):
                log(
                    "[Mailparser] {}{}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "The number of mailparser_dl_ids_for_login or airtable base ids do not match with customerids"
                        ),
                        log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                    )
                )
                exit(1)
            login_pin_sender = "Mailparser"
            renew_pin_sender = "ZapierAirtable"
            login_pin_sender_ids = mailparser_dl_ids_for_login
            renew_pin_sender_ids = base_ids
        elif LOGIN_PIN_SENDER == "ZapierAirtable" and RENEW_PIN_SENDER == "ZapierAirtable":
            base_ids = AIRTABLE_BASE_IDS.strip().split()
            if len(base_ids) != len(user_list):
                log(
                    "[Mailparser] {}{}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "The number of airtable base ids do not match with customerids"
                        ),
                        log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                    )
                )
                exit(1)
            login_pin_sender = "ZapierAirtable"
            renew_pin_sender = "ZapierAirtable"
            login_pin_sender_ids = base_ids
            renew_pin_sender_ids = base_ids
        elif LOGIN_PIN_SENDER == "ZapierAirtable" and RENEW_PIN_SENDER == "Mailparser":
            base_ids = AIRTABLE_BASE_IDS.strip().split()
            mailparser_dl_ids_for_renew = MAILPARSER_DL_IDS_FOR_RENEW.strip().split()
            if len(base_ids) != len(user_list) or len(mailparser_dl_ids_for_renew) != len(user_list):
                log(
                    "[Mailparser] {}{}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "The number of airtable base ids or mailparser_dl_ids_for_renew do not match with customerids"
                        ),
                        log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                    )
                )
                exit(1)
            login_pin_sender = "ZapierAirtable"
            renew_pin_sender = "Mailparser"
            login_pin_sender_ids = base_ids
            renew_pin_sender_ids = mailparser_dl_ids_for_renew
        else:
            log(
                "{}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)(
                        "Configuration Error"
                    )
                )
            )
            exit(1)
        

        for i in range(len(user_list)):
            print("*" * 30)
            log(
                "[EUserv] {}{}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)(
                        "Renewing the @@@ account"
                    ).replace("@@@", ordinal(i + 1)),
                    log_lang_options.get(LOG_LANG, lambda x: x)("..."),
                )
            )
            sessid, s = self.login(user_list[i], passwd_list[i], login_pin_sender, login_pin_sender_ids[i])
            if sessid == "-1":
                log(
                    "[EUserv] {}{} {}{}".format(
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "The @@@ account login failed"
                        ).replace("@@@", ordinal(i + 1)),
                        log_lang_options.get(LOG_LANG, lambda x: x)(","),
                        log_lang_options.get(LOG_LANG, lambda x: x)(
                            "please check the login information"
                        ),
                        log_lang_options.get(LOG_LANG, lambda x: x)("."),
                    )
                )
                continue
            SERVERS = self.get_servers(sessid, s)
            log(
                "[EUserv] {} {}{} {}{}".format(
                    log_lang_options.get(LOG_LANG, lambda x: x)(
                        "The @@@ account is detected"
                    ).replace("@@@", ordinal(i + 1)),
                    log_lang_options.get(LOG_LANG, lambda x: x)("with @@@ VPS").replace(
                        "@@@", str(len(SERVERS))
                    ),
                    log_lang_options.get(LOG_LANG, lambda x: x)(","),
                    log_lang_options.get(LOG_LANG, lambda x: x)(
                        "renewals are being attempted"
                    ),
                    log_lang_options.get(LOG_LANG, lambda x: x)("..."),
                )
            )
            for k, v in SERVERS.items():
                if v:
                    if not self.renew(
                        sessid, s, passwd_list[i], k, renew_pin_sender, renew_pin_sender_ids[i]
                    ):
                        log(
                            "[EUserv] {}{} {} {}{}".format(
                                log_lang_options.get(LOG_LANG, lambda x: x)("ServerID"),
                                log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                                k,
                                log_lang_options.get(LOG_LANG, lambda x: x)("renew Error"),
                                log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                            )
                        )
                    else:
                        log(
                            "[EUserv] {}{} {} {}{}".format(
                                log_lang_options.get(LOG_LANG, lambda x: x)("ServerID"),
                                log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                                k,
                                log_lang_options.get(LOG_LANG, lambda x: x)(
                                    "has been successfully renewed"
                                ),
                                log_lang_options.get(LOG_LANG, lambda x: x)("!"),
                            )
                        )
                else:
                    log(
                        "[EUserv] {}{} {} {}{}".format(
                            log_lang_options.get(LOG_LANG, lambda x: x)("ServerID"),
                            log_lang_options.get(LOG_LANG, lambda x: x)(":"),
                            k,
                            log_lang_options.get(LOG_LANG, lambda x: x)(
                                "does not need to be renewed"
                            ),
                            log_lang_options.get(LOG_LANG, lambda x: x)("."),
                        )
                    )
            time.sleep(15)
            self.check(sessid, s)
            time.sleep(5)


def lambda_handler(event, context):
    EUserv(customer_ids=CUSTOMERIDS, passwords=PASSWORDS).compute()
    
    TG_BOT_TOKEN and TG_USER_ID and TG_API_HOST and telegram()
    RECEIVER_EMAIL and YD_EMAIL and YD_APP_PWD and email()
    SERVER_CHAN_SENDKEY and server_chan()

    print("*" * 30)


if __name__ == "__main__":
    lambda_handler(None, None)
