# BizPartnerCheck
BizPartnerCheck is a web application and REST API that helps construction companies in Austria check their business partners before signing a contract.

## Why this project exists
Before a construction company hires another company, it has to check several things and must be able to prove that it did so. Today these checks are done by hand on many different websites. BizPartnerCheck brings all checks together in one place and saves every Check, so that it can be used as proof later.

## Main features

- **VAT number check** (VIES)
- **Fake company check** (Fake Company List of the Austrian Ministry of Finance)
- **HFU-List check**
- **Austrian Company Register check** (registered company information)
- **Business license check** (GISA)
- **Additional risk information** (financial risks and connections to fake companies)
- **Saved Checks**: results are stored and can be reviewed later
- **REST API** with API tokens, so other software can use the checks
- **API token management** in the web application (view and revoke tokens)

## External services

| Service | Used for |
|---|---|
| VIES (European Commission) | VAT number validity |
| Fake Company List (Austrian Ministry of Finance) | Fake company check |
| HFU-List (Austrian Social Insurance) | HFU-List status |
| Austrian Company Register (Ministry of Justice) | Company registration information |
| GISA | Business registration and license information |
