#!/usr/bin/env python
from pysusestudio import pysusestudio

if __name__ == "__main__":

    username = 'username'
    password = 'password' 
    
	# Instantiate with Basic (HTTP) Authentication
    SS = pysusestudio.pySuseStudio(username, password)
    account = SS.getAccount()
    
    print account