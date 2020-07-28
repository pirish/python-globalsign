# Python Globalsign

Python module to interact with global sign api.  Works for both test and production environments.

## Getting Started

Should be installable with setup_tools. Eventually I will get this into pypi

### Prerequisites

See requirements.txt

```
pip3 install -r requirements.txt
```

### Installing

```
git clone https://github.com/pirish/python-globalsign
cd python-globalsign
python -m virtualenv .venv
. .venv/bin/activate
```

## Running

```
Python 3.7.2 (default, Jan 16 2019, 19:49:22)
[GCC 8.2.1 20181215 (Red Hat 8.2.1-6)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import globalsign
>>> gs =  globalsign.GlobalsignMSSL()
>>> response = gs.get_domains(domain='existingdomain.com')
>>> prof_id = response['DomainDetails']['DomainDetail'][0]['MSSLProfileID']
>>> gs.add_domain_to_profile(domain='newdomain.com', prof_id=prof_id)
{
    'OrderResponseHeader': {
        'SuccessCode': 0,
        'Errors': None,
        'Timestamp': '2020-07-27T22:36:18.059-05:00'
    },
    'MSSLDomainID': 'DSMSXXXXXXXXXXXXX',
    'MetaTag': '<meta name="_globalsign-domain-verification" content="KN2D9txgzkMGq76srtghetyjedtuyhj4VXzEJv0Hy" />',
    'DnsTXT': '_globalsign-domain-verification=KN2D9txgzkMGq76srtghetyjedtuyhj4VXzEJv0Hy'
}
>>>
```
