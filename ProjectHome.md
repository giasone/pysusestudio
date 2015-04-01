This is a Python library that works with the Suse Studio API. This libraries uses XML-RPC, that’s not necessarily good but I just thought it fit better in to Python since XML-RPC is part of the standard python library. The format that the API functions return is a nested dictionary, it might change later to something more palatable.
Other features include a streamlined authentication process and an integrated upload method.
Anyway, this whole library came to be because I am working on a Suse Studio client that I will be releasing shortly i think. Here is how it works:

```

from pysusestudio import pysusestudio

username = 'myusername'
password = 'mypassword' 
    
# Instantiate with Basic (HTTP) Authentication
objSS = pysusestudio.pySuseStudio(username, password)

# This returns the Account information
account = objSS.getAccount()

print account

```



Sponsored by [![](http://www.jasone.it/logo/logo.png)](http://www.jasone.it/)