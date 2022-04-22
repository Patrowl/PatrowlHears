# Configuration required for ADFS

## Configure your ADFS for PatrowlHears

A very good step by step guide can be found [on this website](https://django-auth-adfs.readthedocs.io/en/latest/config_guides.html).
At the end of the guide it also shows how you can retrieve the variables you will use in the next section to configure the Django App that will use your ADFS.

## Variables you need to set on PatrowlHears

There are some variables that you'll need to set in PatrowlHears'settings file that is found at `PatrowlHears/backend_app/backend_app/settings.py`:

Here is the section that you will have to edit

```
# adfs section
AUTH_ADFS = {
    "SERVER": "adfs.example.com",
    "CLIENT_ID": "487d8ff7-80a8-4f62-b926-c2852ab06e94",
    "RELYING_PARTY_ID": "web.example.com",
    "AUDIENCE": "microsoft:identityserver:web.example.com",
    "CA_BUNDLE" : False,
    "CLAIM_MAPPING": {"first_name": "given_name",
                      "last_name": "family_name",
                      "email": "email"},
    "USERNAME_CLAIM": "winaccountname",
    "GROUPS_CLAIM": "group"
}
```

Let's run into each variable and explain what is their role :
- SERVER: this where you will type the domain name of your ADFS that the app will use to resolve it.
- CLIENT_ID: For PatrowlHears to use your ADFS you will have to supply the Client ID you generated from your ADFS.
- RELYING_PARTY_ID: This is the identifier you have entered while creating a relying party id in the section above, you may find it by running the following command in your powershell terminal : `Get-AdfsWebApiApplication | select Identifier | Format-List`
- AUDIENCE: this will set the `aud` claim in your JWT and you can look it up using `Get-AdfsRelyingPartyTrust`, the value you are looking for is `Identifier`
- CA_BUNDLE: if you set this variable to false, which we don't recommend for production, it will bypass any check done on your ADFS certificate. If you set it to true it will use the default CA bundle of the python package `requests`. However if you wish to use a path to your CA bundle you can specify it in this variable as well.
- CLAIM_MAPPING: is used to link the fields of both ADFS and Django users, we recommend to leave it like the `django-auth-adfs` library suggests
- USERNAME_CLAIM: this will be `winaccountname` for ADFS and `upn` for Azure AD. It defines the username claim in JWT sent by the ADFS if the user doesn't exist yet.
- GROUPS_CLAIM: this will be `group` for ADFS and `groups` for Azure AD. It will be in claims of your JWT sent by the ADFS. If an entry in this claim matches a group configured in Django, the user will join it automatically
