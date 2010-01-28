#!/usr/bin/env python

"""
    Copyright (C) 2009 Gianluca Urgese    
    
	pySuseStudio is an up-to-date library for Python that wraps the Suse Studio API.
	I don't know if there are other Python Suse Studio API libraries, and if there
	this is another one. Here's hoping this helps.

	
	Questions, comments? g.urgese@jasone.it

    pySuseStudio is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    pySuseStudio is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pySuseStudio.  If not, see <http://www.gnu.org/licenses/>.
    
"""

__license__ = 'GPL v.2 http://www.gnu.org/licenses/gpl.txt'
__author__ = "Gianluca Urgese <g.urgese@jasone.it>"
__version__ = '0.4'

import httplib, urllib, urllib2, mimetypes, mimetools, httplib2

from urlparse import urlparse
from urllib2 import HTTPError

try:
	import simplejson
except ImportError:
	try:
		import json as simplejson
	except ImportError:
		try:
			from django.utils import simplejson
		except:
			raise Exception("pySuseStudio requires the simplejson library (or Python 2.6) to work. http://www.undefined.org/python/")
			

"""pySuseStudio - Easy Suse Studio API client in Python"""


class pySuseStudioError(Exception):
	def __init__(self, msg, error_code=None):
		self.msg = msg
		if error_code == 400:
			raise APILimit(msg)
	def __str__(self):
		return repr(self.msg)

class APILimit(pySuseStudioError):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

class AuthError(pySuseStudioError):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return repr(self.msg)

class pySuseStudio:
	def __init__(self, username = None, password = None, headers = None, address = 'http://susestudio.com/api/v1'):
		"""pySuseStudio( username = None, password = None, headers = None)

			Instantiates an instance of pySuseStudio. Takes optional parameters for authentication and such (see below).

			Parameters:
				username - Your Suse Studio username, if you want Basic (HTTP) Authentication.
				password - Your Suse Studio secret key, if you want Basic (HTTP) Authentication.
				headers - User agent header.
		"""
		self.authenticated = False
		self.username = username
		self.password = password
		self.address = address

		# get address for authentication
		auth_addr = urlparse(self.address)
		self.auth_address = str(auth_addr.scheme) +'://'+ str(auth_addr.netloc)

		# Check and set up authentication
		if self.username is not None and password is not None:
			# Assume Basic authentication ritual
			self.auth_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
			self.auth_manager.add_password(None, self.auth_address, self.username, password)
			self.handler = urllib2.HTTPBasicAuthHandler(self.auth_manager)
			self.opener = urllib2.build_opener(self.handler)
			if headers is not None:
				self.opener.addheaders = [('User-agent', headers)]
			try:
				#simplejson.load(self.opener.open("http://susestudio.com/api/v1/user/account"))
				self.authenticated = True
			except HTTPError, e:
				raise pySuseStudioError("Authentication failed with your provided credentials. Try again? (%s failure)" % `e.code`, e.code)
		else:
			pass

	def buildApiURL(self, base_url, params):
		return base_url + "?" + "&".join(["%s=%s" %(key, value) for (key, value) in params.iteritems()])

	# Account information
	def getAccount(self):
		"""getAccount()

			Returns information about the account, such as username, email address and disk quota.
		"""
		try:
			if self.authenticated is True:
				return self.opener.open(self.address+'/user/account').read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on your account.")
		except HTTPError, e:
			raise pySuseStudioError("It seems that there's something wrong. You got %s error code; are you doing something you shouldn't be?" % `e.code`, e.code)

	def getApiKey(self):
		"""getApiKey()

			Returns an HTML page which contains the API key flagged as:

			<span class="studio:api_key">ksdjfu93r</span>. 
            
		"""
		try:
			if self.authenticated is True:
				return self.opener.open(self.address+'/user/show_api_key').read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on your account.")
		except HTTPError, e:
			raise pySuseStudioError("getApiKey() failed with a %s error code." % `e.code`)

	# Template sets
	def getTemplateSets(self, name = None):
		"""getTemplateSets(name = None)

			List all template sets.
			Template sets are used to group available templates by topic. The 'default'
			template set contains all vanilla SUSE templates, 'mono' contains those that
			are optimized to be used for mono applications, for example. 
            
			Parameters:
			    name - Optional. Name of template

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/template_sets/'
				if name is not None:
				    url = url + name

				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on template sets.")
		except HTTPError, e:
			raise pySuseStudioError("getTemplateSets() failed with a %s error code." % `e.code`)
			
	# Appliances
	def getAppliances(self, id = None, status = False):
		"""getAppliances(id = None, status = False)

			List all appliances of the current user.  
            
            Parameters:
                id - Optional. Id of the appliance
                status - Optional. If true get status of given Id appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'
				if id is not None:
				    url = url + id
				if status is True:
				    url = url + "/status/"
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on appliances.")
		except HTTPError, e:
			raise pySuseStudioError("getAppliances() failed with a %s error code." % `e.code`)

	def setAppliances(self, clone_from, name=None, arch=None):
		"""setAppliances(clone_from, name, arch)

			Create a new appliance by cloning a template or another appliance with the id appliance_id. 
            If name is left out, a name will be generated. If arch is left out a i686 appliance will be created.  
            POST /api/v1/user/appliances?clone_from=<appliance_id>&name=<name>&arch=<arch>
            Parameters:
                clone_from - The template the new appliance should be based on. 
                name (optional) - The name of appliance 
                arch (optional) - The architecture of the appliance (x86_64 or i686) 

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances'
				data = "clone_from="+str(clone_from)
				if name is not None:
				    data = data + '&name=' + name
				if arch is not None:
				    data = data + "&arch=" + arch
				
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on appliances.")
		except HTTPError, e:
			raise pySuseStudioError("setAppliances() failed with a %s error code." % `e.code`)
	
	def delAppliances(self, id):
		"""delAppliances(self, id)

			Delete appliance with given id. 
            
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password)  
				response, xml = client.request(url, 'DELETE')
				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to get info on appliances.")
		except HTTPError, e:
			raise pySuseStudioError("delAppliances() failed with a %s error code." % `e.code`)
			
	# Repositories
	def getRepositories(self, id):
		"""getRepositories(id)

			List all repositories for the given id appliance.  
            
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/repositories'
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on Repositories.")
		except HTTPError, e:
			raise pySuseStudioError("getRepositories() failed with a %s error code." % `e.code`)
			
	def putRepositories(self, id):
		"""putRepositories(id)

			Update the list of repositories of the given id appliance.  
            
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/repositories'
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'PUT')

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to put info on Repositories.")
		except HTTPError, e:
			raise pySuseStudioError("putRepositories() failed with a %s error code." % `e.code`)
			
	def setRepositories(self, id, repo_id):
		"""setRepositories(id, repo_id)

            Add the specified repository to the given id appliance
            
            Parameters:
                id - Id of the appliance
                repo_id - Id of the repository

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/add_repository'
				data = "repo_id="+str(repo_id)
				
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to insert new Repositories.")
		except HTTPError, e:
			raise pySuseStudioError("setRepositories() failed with a %s error code." % `e.code`)
			
	def delRepositories(self, id, repo_id):
		"""delRepositories(id, repo_id)

            Remove the specified repository to the given id appliance
            
            Parameters:
                id - Id of the appliance
                repo_id - Id of the repository

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/remove_repository?repo_id='+str(repo_id)
				
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'DELETE')
				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to remove Repositories.")
		except HTTPError, e:
			raise pySuseStudioError("delRepositories() failed with a %s error code." % `e.code`)
			
	def addRepositoryUser(self, id):
		"""addRepositoryUser(id)

            Adds the according user repository (the one containing the uploaded RPMs) to the appliance
            
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/add_user_repository'
				data = ""
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to add user to Repository.")
		except HTTPError, e:
			raise pySuseStudioError("addRepositoryUser() failed with a %s error code." % `e.code`)
			
	# Software
	def getSoftware(self, id):
		"""getSoftware(id)

			List all the software for the given id appliance.  
            
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/software'
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on software.")
		except HTTPError, e:
			raise pySuseStudioError("getSoftware() failed with a %s error code." % `e.code`)


	def putSoftware(self, id):
		"""putSoftware(id)

			Update the list of repositories of the given id appliance.  
            
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/software'
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'PUT')

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to put info.")
		except HTTPError, e:
			raise pySuseStudioError("putSoftware() failed with a %s error code." % `e.code`)

			
	def getSoftwareInstalled(self, id, build_id = None):
		"""getSoftwareInstalled(id, build_id)

			List all packages and patterns that are installed. You can either specify the 
			appliance with the id parameter, which will list the software 
			that will installed with the next build or via an build id. That makes it possible 
			to retrieve the installed software for older builds.   
            
            Parameters:
                id - Id of the appliance
                build_id (optional) - Id of the build.

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/installed'
				if build_id is not None:
				    url = url + "?build_id=" + build_id
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on installed software.")
		except HTTPError, e:
			raise pySuseStudioError("getSoftwareInstalled() failed with a %s error code." % `e.code`)
			

	def addSoftwarePackage(self, id, name, version=None, repository_id=None):
		"""addSoftwarePackage(id, name, version=None, repository_id=None)

            Add specified package to the given appliance
            
            Parameters:
                id - Id of the appliance
                name - Name of the package
                version (optional) - Version of the package
                repository_id (optional) - Repository to pick the package from

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/add_package'
				data = "name="+str(name)
				if version is not None:
				    data = data + '&version=' + str(version)
				if repository_id is not None:
				    data = data + "&repository_id=" + str(repository_id)
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to add package to Repository.")
		except HTTPError, e:
			raise pySuseStudioError("addSoftwarePackage() failed with a %s error code." % `e.code`)
			
	def delSoftwarePackage(self, id, name):
		"""delSoftwarePackage(id, name)

            Delete specified package from the given appliance
            
            Parameters:
                id - Id of the appliance
                name - Name of the package

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/remove_package'
				data = "name="+str(name)

				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to remove package from Repository.")
		except HTTPError, e:
			raise pySuseStudioError("delSoftwarePackage() failed with a %s error code." % `e.code`)
			
		
	def addSoftwarePattern(self, id, name, version=None, repository_id=None):
		"""addSoftwarePattern(id, name, version=None, repository_id=None)

            Add specified pattern to the given appliance
            
            Parameters:
                id - Id of the appliance
                name - Name of the pattern
                version (optional) - Version of the pattern
                repository_id (optional) - Repository to pick the pattern from

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/add_pattern'
				data = "name="+str(name)
				if version is not None:
				    data = data + '&version=' + str(version)
				if repository_id is not None:
				    data = data + "&repository_id=" + str(repository_id)
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to add pattern to Repository.")
		except HTTPError, e:
			raise pySuseStudioError("addSoftwarePattern() failed with a %s error code." % `e.code`)
			
			
	def delSoftwarePattern(self, id, name):
		"""delSoftwarePattern(id, name)

            Delete specified pattern from the given appliance
            
            Parameters:
                id - Id of the appliance
                name - Name of the pattern

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/remove_pattern?name='+str(name)
                
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'DELETE')

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to remove pattern from Repository.")
		except HTTPError, e:
			raise pySuseStudioError("delSoftwarePattern() failed with a %s error code." % `e.code`)
			

			
	def banSoftwarePackage(self, id, name):
		"""banSoftwarePackage(id, name)

            Ban specified package from the given appliance
            
            Parameters:
                id - Id of the appliance
                name - Name of the package

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/ban_package'
				data = "name="+str(name)

				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to ban package from appliance.")
		except HTTPError, e:
			raise pySuseStudioError("banSoftwarePackage() failed with a %s error code." % `e.code`)
			
			
	def unbanSoftwarePackage(self, id, name):
		"""unbanSoftwarePackage(id, name)

            Unban specified package from the given appliance
            
            Parameters:
                id - Id of the appliance
                name - Name of the package

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/cmd/unban_package'
				data = "name="+str(name)

				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to unban package from appliance.")
		except HTTPError, e:
			raise pySuseStudioError("unbanSoftwarePackage() failed with a %s error code." % `e.code`)
			
			
			


	def searchSoftware(self, id, q, all_fields='false', all_repos='false'):
		"""searchSoftware(id, q, all_fields='false', all_repos='false')

            Search all software that matches the given search string. If the all_fields
            parameter is set to true all fields are considered, otherwise only the name of the package 
            or pattern is matched against the search_string. 
            By default only software that is available to the appliance is considered, e.g. the search is limited to the 
            repositories of this appliances. If you want to search in all repositories set the all_repos parameter to 
            true
            
            Parameters:
                id - Id of the appliance
                q - The search string 
                all_fields (optional) - Option to perform the search on all fields. Default is 'false'
                all_repos (optional) - Option to perform the search on all repositories. Default is 'false'

        
		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/software/search'
				url = url +"?q="+str(q)
				if all_fields == 'true':
				    url = url + '&all_fields=true'
				if all_repos == 'true':
				    url = url + "&all_repos=true"

				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to search software in a Repository.")
		except HTTPError, e:
			raise pySuseStudioError("searchSoftware() failed with a %s error code." % `e.code`)
		

	# Image files
	def getImageFiles(self, id, build_id, path):
		"""getImageFiles(id, build_id, path)

			Returns the file with the given path from an image.   
            
            Parameters:
                id - Id of the appliance
                build_id - Id of the build.
		path - Path to the file in the built appliance
		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/image_files?build_id='+str(build_id)+'&path='+str(path)
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get files from an image.")
		except HTTPError, e:
			raise pySuseStudioError("getImageFiles() failed with a %s error code." % `e.code`)
			
			
	# GPG Keys
	def getGPGKeys(self, id):
		"""getGPGKeys(id)

			List all the GPG keys for the given id appliance.  
            
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/gpg_keys'
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get GPG keys from an appliance.")
		except HTTPError, e:
			raise pySuseStudioError("getGPGKeys() failed with a %s error code." % `e.code`)


	def getGPGKey(self, id, key_id):
		"""getGPGKey(id, key_id)

			Shows information on the GPG key with the id key_id.  
            
            Parameters:
                id - Id of the appliance
		key_id - Id of the GPG key

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/gpg_keys/'+str(key_id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info from a GPG key.")
		except HTTPError, e:
			raise pySuseStudioError("getGPGKey() failed with a %s error code." % `e.code`)

			
	def setGPGKey(self, id, name, target, key = None):
		"""setGPGKey(id, name, target, key)

            Uploads a GPG key to the appliance with the given id. The key can either be given as the key parameter 
	    or wrapped as with form-based file uploads in HTML (RFC 1867) in the body of the POST request. 
	    The key will be imported into the keyring that is specified in the target parameter
            
            Parameters:
                id - Id of the appliance
                name - A name for the key
		target - The target specifies in which keyring the key will be imported. Possible values are: 'rpm'
		key (optional) - The URL encoded key

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/gpg_keys'
				data = "?name="+str(name)
				data = data + "&target="+str(target)
				if key is not None:
				    data = data + '&key=' + str(key)

				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to set a GPG Key for an appliance.")
		except HTTPError, e:
			raise pySuseStudioError("setGPGKey() failed with a %s error code." % `e.code`)
			
	
	def delGPGKey(self, id, key_id):
		"""delGPGKey(self, id, key_id)

			Deletes the GPG key with the id key_id from the appliance. 
            
            Parameters:
                id - Id of the appliance
		key_id - Id of the GPG key

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/appliances/'+str(id)+'/gpg_keys/'+str(key_id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password)  
				response, xml = client.request(url, 'DELETE')
				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to delete a GPG key.")
		except HTTPError, e:
			raise pySuseStudioError("delGPGKey() failed with a %s error code." % `e.code`)
			
			

        # Overlay files
	def getOverlayFiles(self, id):
		"""getOverlayFiles(id)

        List all overlay files of the given id appliance.
        
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/files'
				url = url +"?appliance_id="+str(id)
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on overlay files.")
		except HTTPError, e:
			raise pySuseStudioError("getOverlayFiles() failed with a %s error code." % `e.code`)
			
		
	def addOverlayFiles(self, id, body, filename=None, path=None, owner=None, group=None, permissions=None, enabled=None):
		"""addOverlayFiles(id, body, filename=None, path=None, owner=None, group=None, permissions=None, enabled=None)

            Adds a file to the given id appliance. 
            Optionally, one or more metadata settings can be specified. If those are left out, they 
            can also be change later. 
            
            Parameters:
                id - Id of the appliance
                body - the entity body to be sent with the request.
                filename (optional) - The name of the file in the filesystem. 
                path (optional) - The path where the file will be stored. 
                owner (optional) - The owner of the file. 
                group (optional) - The group of the file. 
                permissions (optional) - The permissions of the file. 
                enabled (optional) - Used to enable/disable this file for the builds. 

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/files?'
				data = "appliance_id="+str(id)
				if filename is not None:
				    data = data + "&filename="+str(filename)
				if path is not None:
				    data = data + '&path=' + str(path)
				if owner is not None:
				    data = data + "&owner=" + str(owner)
				if group is not None:
				    data = data + '&group=' + str(group)
				if permissions is not None:
				    data = data + "&permissions=" + str(permissions)
				if enabled is not None:
				    data = data + '&enabled=' + str(enabled)
				    
				url = url + data
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'POST', body)
				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to add overlay files to Repository.")
		except HTTPError, e:
			raise pySuseStudioError("addOverlayFiles failed with a %s error code." % `e.code`)
			
        
	def getOverlayFile(self, id):
		"""getOverlayFile(id)

        Return overlay file with the given id .
        
            Parameters:
                id - Id of the file

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/files/'+str(id)+'/data'
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to set requested overlay file.")
		except HTTPError, e:
			raise pySuseStudioError("getOverlayFile() failed with a %s error code." % `e.code`)
			
        
	def getOverlayFileMeta(self, id):
		"""getOverlayFileMeta(id)

        Return overlay file meta data with the given id .
        
            Parameters:
                id - Id of the file

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/files/'+str(id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to set metadata on requested overlay file.")
		except HTTPError, e:
			raise pySuseStudioError("getOverlayFileMeta() failed with a %s error code." % `e.code`)


	def putOverlayFile(self, id, body):
		"""putSoftware(id, body)

			Writes the content of the file with given id.  
            
            Parameters:
                id - Id of the file
                body - the entity body to be sent with the request
                
		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/files/'+str(id)+'/data'
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'PUT', body)

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to put file.")
		except HTTPError, e:
			raise pySuseStudioError("putOverlayFile() failed with a %s error code." % `e.code`)


	def putOverlayFileMeta(self, id, body):
		"""putSoftware(id, body)

			Writes the content of the file metadata with given id.  
            
            Parameters:
                id - Id of the file
                body - the entity body to be sent with the request

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/files/'+str(id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'PUT', body)
				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to put file.")
		except HTTPError, e:
			raise pySuseStudioError("putOverlayFile() failed with a %s error code." % `e.code`)


			
	def delOverlayFile(self, id):
		"""delOverlayFile(id)

            Delete specified overlay file
            
            Parameters:
                id - Id of the file

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/files/'+str(id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'DELETE')

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to remove overlay file.")
		except HTTPError, e:
			raise pySuseStudioError("delOverlayFile() failed with a %s error code." % `e.code`)
	

    # Running builds
	def getRunningBuilds(self, id):
		"""getRunningBuilds(id)

        List all running builds for the appliance with the given id .
        
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/running_builds'
				data = "appliance_id="+str(id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to list running builds for a selected appliance.")
		except HTTPError, e:
			raise pySuseStudioError("getRunningBuilds() failed with a %s error code." % `e.code`)
			
        
	def getRunningBuild(self, id):
		"""getRunningBuild(id)

       Show status of the build with the given id .
        
            Parameters:
                id - Id of the build

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/running_builds/'+str(id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get status on requested build.")
		except HTTPError, e:
			raise pySuseStudioError("getRunningBuild() failed with a %s error code." % `e.code`)

		
	def addBuild(self, id, force=None, version=None, image_type=None):
		"""addBuild(id, force=None, version=None, image_type=None)

            Start a new build for the given id appliance. 
            If there already is a build with the same appliance settings (build type and version) 
            an error is returned. In this case a build can be enforced by setting the optional 
            force parameter to true.
            Optionally the appliance version and build type can be set with the version and image_type parameters. 
            
            Parameters:
                id - Id of the appliance
                force (optional) - Force a build even if it overwrites an already existing build. 
                version (optional) - The version of the appliance. 
                image_type (optional) -  The format of the build. Supported are 'xen','oem','vmx' and 'iso'. 

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/running_builds'
				data = "appliance_id="+str(id)
				if force is not None:
				    data = data + "&force="+str(force)
				if version is not None:
				    data = data + '&version=' + str(version)
				if image_type is not None:
				    data = data + "&image_type=" + str(image_type)
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to start a new build.")
		except HTTPError, e:
			raise pySuseStudioError("addBuild failed with a %s error code." % `e.code`)
			
			
	def delRunningBuild(self, id):
		"""delRunningBuild(id)

            Delete specified running build
            
            Parameters:
                id - Id of the running build

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/running_builds/'+str(id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'DELETE')

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to remove running build.")
		except HTTPError, e:
			raise pySuseStudioError("delRunningBuild() failed with a %s error code." % `e.code`)
	
    # Finished builds
	def getCompletedBuilds(self, id):
		"""getCompletedBuilds(id)

        List all completed builds for the appliance with the given id .
        
            Parameters:
                id - Id of the appliance

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/builds'
				data = "appliance_id="+str(id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to list completed builds for a selected appliance.")
		except HTTPError, e:
			raise pySuseStudioError("getCompletedBuilds() failed with a %s error code." % `e.code`)
			
        
	def getCompletedBuild(self, id):
		"""getCompletedBuild(id)

       Show build info of the build with the given id .
        
            Parameters:
                id - Id of the build

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/builds/'+str(id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get status on requested build.")
		except HTTPError, e:
			raise pySuseStudioError("getCompletedBuild() failed with a %s error code." % `e.code`)

			
	def delCompletedBuild(self, id):
		"""delCompletedBuild(id)

            Delete specified completed build
            
            Parameters:
                id - Id of the running build

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/builds/'+str(id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'DELETE')

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to remove requested build.")
		except HTTPError, e:
			raise pySuseStudioError("delCompletedBuild() failed with a %s error code." % `e.code`)
	
	
    # RPM Uploads
	def getRPMs(self, base):
		"""getRPMs(base)

        List all uploaded RPMs for the the given base system.
        
            Parameters:
                base - Base system of the RPM or archive, e.g. 11.1 or SLED11.

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/rpms'
				data = "base_system="+str(base)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to list all uploaded RPMs for a selected base system.")
		except HTTPError, e:
			raise pySuseStudioError("getRPMs() failed with a %s error code." % `e.code`)
			
        
	def getRPMInfo(self, id):
		"""getRPMInfo(id)

       Show information on the uploaded RPM with the given id .
        
            Parameters:
                id - Id of the uploaded RPM

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/rpms/'+str(id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get info on requested RPM.")
		except HTTPError, e:
			raise pySuseStudioError("getRPMInfo() failed with a %s error code." % `e.code`)

        
	def getRPM(self, id):
		"""getRPM(id)

       Returns the RPM with the given id .
        
            Parameters:
                id - Id of the uploaded RPM

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/rpms/'+str(id)+'/data'
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get requested RPM.")
		except HTTPError, e:
			raise pySuseStudioError("getRPM() failed with a %s error code." % `e.code`)
			
		
	def addRPM(self, base):
		"""addBuild(base)

            Adds an RPM or archive to the user repository for appliances base 
            
            Parameters:
                base - Base system of the RPM or archive, e.g. 11.1 or SLED11.
                

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/rpms'
				data = "base_system="+str(base)
				
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to add a new RPM")
		except HTTPError, e:
			raise pySuseStudioError("addRPM() failed with a %s error code." % `e.code`)
	
	
	def putRPM(self, id, body):
		"""putSoftware(id, body)

			Update the content of the RPM or archive with the given id.  
            
            Parameters:
                id - Id of the uploaded RPM. 
                body - the entity body to be sent with the request.

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/rpms/'+str(id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'PUT', body)
				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to update RPM's content.")
		except HTTPError, e:
			raise pySuseStudioError("putRPM() failed with a %s error code." % `e.code`)

			
			
	def delRPM(self, id):
		"""delRPM(id)

            Deletes the RPM or archive with the given id from the user repository
            
            Parameters:
                id - id of the uploaded RPM.

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/rpms/'+str(id)
				client = httplib2.Http(".cache") 
				client.add_credentials(self.username, self.password) 
				response, xml = client.request(url, 'DELETE')

				return xml
			else:
				raise pySuseStudioError("You need to be authenticated to remove RPM.")
		except HTTPError, e:
			raise pySuseStudioError("delRPM() failed with a %s error code." % `e.code`)

    # Repositories
	def getRepositories(self, base=None, filter=None):
		"""getRepositories(base=None, filter=None)

        Returns a list of repositories. If neither base system nor filter are specified all available repositories 
        are returned. 
        When filtering the results with the filter parameter, the repository name, repository url and repository 
        packages are searched.
        
            Parameters:
                base (optional) - Limit the results to repositories with this base system. 
                filter (optional) - Only show repositories matching this search string.

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/repositories'
				#TODO Arguments implementation
				data = ''
				if base is not None:
				    data = data + '&base=' + str(base)
				if filter is not None:
				    data = data + "&filter=" + str(filter)
				
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to list repositories.")
		except HTTPError, e:
			raise pySuseStudioError("getRepositories() failed with a %s error code." % `e.code`)
			
        
	def getRepository(self, id):
		"""getCompletedBuild(id)

       Show information on the repository with the given id .
        
            Parameters:
                id - Id of the repository.

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/repositories/'+str(id)
				
				return self.opener.open(url).read()
			else:
				raise pySuseStudioError("You need to be authenticated to get information on requested repository.")
		except HTTPError, e:
			raise pySuseStudioError("getRepository() failed with a %s error code." % `e.code`)

			
	def addRepository(self, repo_url, name):
		"""addRepository(repo_url, name)

            Imports a new repository into Studio. Returns the metadata for the created repository
            
            Parameters:
                repo_url - Base url of the repository. 
                name - Name for the repository. 

		"""
		try:
			if self.authenticated is True:
				url = self.address+'/user/repositories'
				data = "url="+str(repo_url)+ '&name=' + str(name)
				
				return self.opener.open(url, data).read()
			else:
				raise pySuseStudioError("You need to be authenticated to add a new repository.")
		except HTTPError, e:
			raise pySuseStudioError("addRepository() failed with a %s error code." % `e.code`)
	
			
	def version(self):
		"""version()

            Print version information

		"""
		try:
			print "pySuseStudio v."+ __version__+" - Author: "+__author__
			print "released under "+ __license__

		except HTTPError, e:
			raise pySuseStudioError("version() failed with a %s error code." % `e.code`)
	


    
