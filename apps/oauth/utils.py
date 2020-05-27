# -*- coding: utf-8 -*-
from django.conf import settings

from .constants import ACCESS_TOKEN_EXPIRES
from utils.signature import BaseSignature

class SignAccessToken(BaseSignature):

    secret_key = settings.SECRET_KEY
    expiry = ACCESS_TOKEN_EXPIRES


