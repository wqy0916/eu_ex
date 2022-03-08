# eu_ex

eu_ex means EUserv_extend. A Python script which can help you renew your free EUserv IPv6 VPS.

This script can check the VPS amount in your account automatically and renew the VPS if it can be renewed.

## Caveats

Please do not abuse this script to cause EUserv to be overloaded and lose connection frequently or to advertise on YouTube and other media for your own benefit. Otherwise I will delete this repositery like previous `a-beam-of-light/eu_ex`or keep it private.

## Dependencies

`python3 -m pip install requests beautifulsoup4 pyairtable` or

`python3 -m pip install -r requirements.txt`

## References

### EUserv "EUserv - Attempted Login" original mail

```
From: EUserv Support <support@euserv.de>
To：  xyz@example.com
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
From：	     EUserv Support <support@euserv.de>
To：	         xyz@example.com
Subject：	 EUserv - PIN for the Confirmation of a Security Check
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



**NOTE**. Detailed documentation will be completed in the near future.
