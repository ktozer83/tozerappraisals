from django.contrib.auth.hashers import BasePasswordHasher, mask_hash

from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes, force_text
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_noop as _

from django.contrib.auth.models import User
from django.db import models

import hashlib
import random
import bcrypt

class CustomBcryptPasswordHasher(BasePasswordHasher):
    
    algorithm = "bcrypt_cust"
    rounds = 12
    
    # md5 passwords due to legacy passwords being md5
    def md5(self, password):  
        md5_pass = hashlib.md5(password).hexdigest()

        return md5_pass
    
    # generate salt
    def salt(self):
        return bcrypt.gensalt(self.rounds)
    
    # hash password    
    def encode(self, password, salt):  
        salt2 = self.salt()
        password = force_bytes(password)
        
        data = bcrypt.hashpw(self.md5(password) + salt2, salt)

        #return salt and crypted password
        return "%s$%s%%%s" % (self.algorithm, force_text(data), force_text(salt2))
    
    # verify password    
    def verify(self, password, encoded):
        #bcrypt = self._load_library()
        algorithm, data = encoded.split('$', 1)
        data_pass, data_salt = data.split('%', 1)
        password = self.md5(password)
        assert algorithm == self.algorithm
            
        #compare the crypt of input+stored_salt2 to the stored crypt password
        return constant_time_compare(data_pass, bcrypt.hashpw(password + data_salt, data_pass))
            
    def safe_summary(self, encoded):
        algorithm, empty, algostr, work_factor, data = encoded.split('$', 4)
        assert algorithm == self.algorithm
        data_pass, data_salt = data.split('%', 1)
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('work factor'), work_factor),
            (_('salt'), mask_hash(data_pass)),
            (_('checksum'), mask_hash(data_salt)),
        ])
