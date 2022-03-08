# Changelog

## v2022.03.04

EUserv KundenCenter (2.17.1_20220228)

- Receive login PIN(6-digits) using zapier parsed data & airtable
  workflow: auto-forward your EUserv PIN email to your zapier mail parser inbox 
  -> parsing PIN via zapier mail parser -> send parsed PIN to airtable.

## v2021.12.15

- Implemented a simple localization system, log output localization
- Reformat code via black
## v2021.11.26

- Handle TrueCaptcha service exception
- Adjust TrueCaptcha constraint parameters for high availability.
  Plus, the CAPTCHA of EUserv is currently case-insensitive, so the above adjustment works.
  
## v2021.11.06

EUserv KundenCenter (2.16.4_20211031)

- Receive renew PIN(6-digits) using mailparser parsed data download url
  workflow: auto-forward your EUserv PIN email to your mailparser inbox 
  -> parsing PIN via mailparser -> get PIN from mailparser
- Update kc2_security_password_get_token request

## v2021.09.30

- Captcha automatic recognition using TrueCaptcha API
- Email notification
- Add login failure retry mechanism
- reformat log info