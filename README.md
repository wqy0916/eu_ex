# eu_ex

eu_ex means EUserv_extend. A Python script which can help you renew your free EUserv IPv6 VPS.

This script can check the VPS amount in your account automatically and renew the VPS if it can be renewed.

## Caveats

Please do not abuse this script to cause EUserv to be overloaded and lose connection frequently or to advertise on YouTube and other media for your own benefit. Otherwise I will delete this repositery like previous `a-beam-of-light/eu_ex` or keep it private.

## Project Structure

- `main.py`: (required) the main program for auto-renewing free EUserv IPv6 VPS.
- `locales.py`: (optional) translations for `main.py` log. If this file is not added, the log will be displayed in English.
- `requirements.txt`: project dependency description file.

## How it works
EUserv set the first threshold from the end of September 2021, that is, the login CAPTCHA (successful verification status maintained for 24 hours), so from now on, we use the API provided by TrueCaptcha (there is a free amount every day) to identify. Not long after, about the beginning of November 2021, EUserv set a second threshold, which is the email PIN verification when renewing. Nearly four months later, on February 28, 2022, EUserv set another threshold, the email PIN verification for each login.

For login CAPTCHA, the API provided by TrueCaptcha is currently used and will be replaced with a locally trained model in the future (see [eu_img](https://github.com/bitsavers/eu_img) for details).

For email PIN, two methods are provided.
  1. zapier mail parser + airtable: get email PIN from zapier mail parser via airtable API automatically.
  2. mailparser: convert the parsed data from email into HTTP REST API to get PIN automatically.

Email Parser Services:
  1. [Zapier Emails Parser](https://parser.zapier.com)
  2. [Mailparser](https://mailparser.io)
  3. [Parseur](https://parseur.com)
  4. https://zapier.com/blog/best-email-parser/

## Dependencies

`python3 -m pip install requests beautifulsoup4 pyairtable` or

`python3 -m pip install -r requirements.txt`

Tips. If you deploy it as a severless function, e.g. AWS Lambda, you need to package the dependencies along with the source code.

## Setup

### Environment Variable Setting
`CUSTOMERIDS`: (required) EUserv customer ids, it supports multiple accounts, must use one space to separate multiple accounts. DO NOT USE your EUserv account email address, USE custom id instead.

`PASSWORDS`: (required) EUserv customer passwords, it supports multiple accounts, must use one space to separate multiple accounts.

`TRUECAPTCHA_USERID`: (optional) TrueCaptcha service to solve CAPTCHA. Its default value is TrueCaptcha demo user id, recommended to set to use your own.

`TRUECAPTCHA_APIKEY`: (optional) TrueCaptcha service to solve CAPTCHA. Its default value is TrueCaptcha demo api key, recommended to set to use your own.

`AIRTABLE_API_KEY`: If you want to adopt `zapier mail parser + airtable` to get email PIN(login or renew), it's required. Otherwise it's optional.

`AIRTABLE_BASE_IDS`: If you want to adopt `zapier mail parser + airtable` to get email PIN(login or renew), it's required. Otherwise it's optional.

`MAILPARSER_DL_IDS_FOR_LOGIN`: If you want to adopt `mailparser` to get email PIN(login), it's required. Otherwise it's optional.

`MAILPARSER_DL_IDS_FOR_RENEW`: If you want to adopt `mailparser` to get email PIN(renew), it's required. Otherwise it's optional.

`RECEIVER_EMAIL`: (optional) receive emails for email notifications.

`YD_EMAIL`: (optional) yandex email notifications sender email address.

`YD_APP_PWD`: (optional) yandex email notifications sender app password.

`SERVER_CHAN_SENDKEY`: (optional) Server Chan notifications.

### Constant Variable Setting
`CHECK_CAPTCHA_SOLVER_USAGE`: checking TrueCaptcha API usage, options can be `True` or `False`, default is `True`.

`LOGIN_PIN_SENDER`: it depends on which way you choose to get the email pin for login. options can be `ZapierAirtable` or `Mailparser`, default is `ZapierAirtable`.

`RENEW_PIN_SENDER`: it depends on which way you choose to get the email pin for renew. options can be `ZapierAirtable` or `Mailparser`, default is `ZapierAirtable`.

`AIRTABLE_TABLE_NAME_FOR_LOGIN`: airtable name for receiving login pin. its value is `Login`, it is not recommended to change this value anymore, unless you know what you are going to do.

`AIRTABLE_TABLE_NAME_FOR_RENEW`: airtable name for receiving login pin. its value is `Renew`, it is not recommended to change this value anymore, unless you know what you are going to do.

`WAITING_TIME_OF_PIN`: waiting time of receiving PIN, units are seconds. default is `12`.

`LOGIN_MAX_RETRY_COUNT`: maximum number of login retry. default is `5`.

`TG_BOT_TOKEN`: telegram bot token for notifications via telegram.

`TG_USER_ID`: telegram user, group or channel id for notifications via telegram.

`TG_API_HOST`: telegram api host, default is `https://api.telegram.org`, it is not recommended to change this value anymore, unless you know what you are going to do.

### Mail Forwarding
Set up automatic mail forwarding to `mailparser` or `zapier mail parser` inboxes for login/renew pin emails. It is possible for non-gmail mailboxes to receive emails from EUserv, provided that they can be received.

For login pin email, you can refer to the content of `EUserv "Esserv - Attempted Login" original email` in `References`.

For renew pin email, you can refer to the content of `EUserv "EUserv - PIN for the Confirmation of a Security Check" original mail` in `References`.

### Multi-account eMail Forwarding Setting Principles
  1. One inbox of `mailparser` corresponds to the login or renew of an euserv account. 
  2. One base of `airtable` corresponds to one euserv account (login and renew are already included, no need to split the usage). 

### Mailparser Setting
see [Mailparser](./docs/Mailparser.md).

### Zapier + Airtable Setting
see [ZapierAirtable](./docs/ZapierAirtable.md). This approach is recommended.

### How to run

`python3 main.py` or

Lambda function handler name: `main.lambda_handler`

## References

### EUserv "EUserv - Attempted Login" original mail

```
From: EUserv Support <support@euserv.de>
To:   xyz@example.com
Subject: EUserv - Attempted Login
Content-Type: text/plain; charset = utf-8

Dear XYZ,

a login into your account at EUserv with the customer id 00000000 has just been attempted. If you have not tried to login then ignore this email.

PIN:
NQX54R


Sincerely,
Your customer support EUserv

--
Web ................: http://www.euserv.com
Login control panel.: https://support.euserv.com
FAQ ................: http://faq.euserv.com
Help & Guides.......: http://wiki.euserv.com
Community / Forum...: http://forum.euserv.com
Mailing-Liste ......: http://www.euserv.com/en/?show_contact=mailinglist
Twitter ............: http://twitter.com/euservhosting
Facebook ...........: http://www.facebook.com/euservhosting
--

EUserv Internet
is a division of
ISPpro Internet KG

Postal address:
ISPpro Internet KG
Division EUserv Internet
P.O. Box 2224
07622 Hermsdorf
GERMANY

Support-Phone: +49 (0) 3641 3101011 (English speaking)

Administration:
ISPpro Internet KG
Neue Str. 4
D-07639 Bad Klosterlausnitz
GERMANY

Management...............: Dirk Seidel
Register.................: AG Jena, HRA 202638
VAT Number...............: 162/156/36600
Tax office ..............: Jena
International VAT Number.: DE813856317
```

### EUserv "EUserv - PIN for the Confirmation of a Security Check" original mail

```
From:	     EUserv Support <support@euserv.de>
To:	         xyz@example.com
Subject:	 EUserv - PIN for the Confirmation of a Security Check
Content-Type: text/plain; charset = utf-8
Dear XYZ,

you have just requested a PIN for confirmation of a security check at EUserv. If you have not requested the PIN then ignore this email.

PIN:
404387

PLEASE NOTE: If you already have requested a new PIN for the same process this PIN is invalid. Also this PIN is only valid within the session in which it has been requested. This means the PIN is invalid if you for example change the browser or if you logout and perform a new login.


Sincerely,
Your customer support EUserv

--
Web ................: http://www.euserv.com
Login control panel.: https://support.euserv.com
FAQ ................: http://faq.euserv.com
Help & Guides.......: http://wiki.euserv.com
Community / Forum...: http://forum.euserv.com
Mailing-Liste ......: http://www.euserv.com/en/?show_contact=mailinglist
Twitter ............: http://twitter.com/euservhosting
Facebook ...........: http://www.facebook.com/euservhosting
--

EUserv Internet
is a division of
ISPpro Internet KG

Postal address:
ISPpro Internet KG
Division EUserv Internet
P.O. Box 2224
07622 Hermsdorf
GERMANY

Support-Phone: +49 (0) 3641 3101011 (English speaking)

Administration:
ISPpro Internet KG
Neue Str. 4
D-07639 Bad Klosterlausnitz
GERMANY

Management...............: Dirk Seidel
Register.................: AG Jena, HRA 202638
VAT Number...............: 162/156/36600
Tax office ..............: Jena
International VAT Number.: DE813856317
```

## Other Implementations
Login to the mailbox to get the email containing EUserv PIN when logging in or renewing:
  1. https://github.com/GGttyyy/Euserv_extend_pin
  2. https://github.com/SAOJSM/EU_CHICK_EXTEND_CHT
