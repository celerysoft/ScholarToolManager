# -*- coding: utf-8 -*-
from enum import Enum, unique


class JwtSub(Enum):
    Activation = 'activation'
    ModifyEmail = 'modify email address'
