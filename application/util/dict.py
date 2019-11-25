# -*- coding: utf-8 -*-
"""
A toolkit for python dict type
"""


class DictToolkit(object):
    @staticmethod
    def merge_dict(original: dict, updates: dict):
        if original is None and updates is None:
            return None

        if original is None:
            return updates
        if updates is None:
            return original

        try:
            merged_dict = original.copy()
            merged_dict.update(updates)
        except (AttributeError, ValueError) as e:
            raise TypeError('original and updates must be a dictionary: %s' % e)

        return merged_dict


dict_toolkit = DictToolkit()
