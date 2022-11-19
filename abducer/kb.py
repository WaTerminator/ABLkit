# coding: utf-8
#================================================================#
#   Copyright (C) 2021 LAMDA All rights reserved.
#   
#   File Name     ：kb.py
#   Author        ：freecss
#   Email         ：karlfreecss@gmail.com
#   Created Date  ：2021/06/03
#   Description   ：
#
#================================================================#

from abc import ABC, abstractmethod
import bisect
import copy
import numpy as np

from collections import defaultdict
from itertools import product

class KBBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_candidates(self):
        pass

    @abstractmethod
    def get_all_candidates(self):
        pass

    @abstractmethod
    def logic_forward(self, X):
        pass
    
    def _length(self, length):
        if length is None:
            length = list(self.base.keys())
        if type(length) is int:
            length = [length]
        return length
    
    def __len__(self):
        pass


class ClsKB(KBBase):
    def __init__(self, pseudo_label_list, kb_max_len = -1):
        super().__init__()
        self.pseudo_label_list = pseudo_label_list
        self.base = {}
        self.kb_max_len = kb_max_len
        
        if(self.kb_max_len > 0):
            X = self.get_X(self.pseudo_label_list, self.kb_max_len)
            Y = self.get_Y(X, self.logic_forward)

            for x, y in zip(X, Y):
                self.base.setdefault(len(x), defaultdict(list))[y].append(np.array(x))
    
    def get_X(self, pseudo_label_list, max_len):
        res = []
        assert(max_len >= 2)
        for len in range(2, max_len + 1):
            res += list(product(pseudo_label_list, repeat = len))
        return res

    def get_Y(self, X, logic_forward):
        return [logic_forward(nums) for nums in X]
    
    def logic_forward(self):
        return None

    def get_candidates(self, key, length = None):
        if(self.base == {}):
            return []
        
        if key is None:
            return self.get_all_candidates()
        
        length = self._length(length)
        if(self.kb_max_len < min(length)):
            return []
        return sum([self.base[l][key] for l in length], [])
    
    def get_all_candidates(self):
        return sum([sum(v.values(), []) for v in self.base.values()], [])

    def _dict_len(self, dic):
        return sum(len(c) for c in dic.values())

    def __len__(self):
        return sum(self._dict_len(v) for v in self.base.values())



class add_KB(ClsKB):
    def __init__(self, kb_max_len = -1):
        self.pseudo_label_list = list(range(10))
        super().__init__(self.pseudo_label_list, kb_max_len)
    
    def logic_forward(self, nums):
        return sum(nums)

    def get_candidates(self, key, length = None):
        return super().get_candidates(key, length)
    
    def get_all_candidates(self):
        return super().get_all_candidates()
    
    def _dict_len(self, dic):
        return super()._dict_len(dic)

    def __len__(self):
        return super().__len__()
    
class hwf_KB(ClsKB):
    def __init__(self, kb_max_len = -1):
        self.pseudo_label_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+', '-', '*', '/']
        super().__init__(self.pseudo_label_list, kb_max_len)
        
    def valid_formula(self, formula):
        if(len(formula) % 2 == 0):
            return False
        for i in range(len(formula)):
            if(i % 2 == 0 and formula[i] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
                return False
            if(i % 2 != 0 and formula[i] not in ['+', '-', '*', '/']):
                return False
        return True
    
    def logic_forward(self, formula):
        if(self.valid_formula(formula) == False):
            return np.inf
        try:
            return round(eval(''.join(formula)), 2)
        except ZeroDivisionError:
            return np.inf
        
    def get_candidates(self, key, length = None):
        return super().get_candidates(key, length)
    
    def get_all_candidates(self):
        return super().get_all_candidates()
    
    def _dict_len(self, dic):
        return super()._dict_len(dic)

    def __len__(self):
        return super().__len__()
    

class RegKB(KBBase):
    def __init__(self, X, Y = None):
        super().__init__()
        tmp_dict = {}
        for x, y in zip(X, Y):
            tmp_dict.setdefault(len(x), defaultdict(list))[y].append(np.array(x))

        self.base = {}
        for l in tmp_dict.keys():
            data = sorted(list(zip(tmp_dict[l].keys(), tmp_dict[l].values())))
            X = [x for y, x in data]
            Y = [y for y, x in data]
            self.base[l] = (X, Y)

    def logic_forward(self):
        return None
              
    def get_candidates(self, key, length = None):
        if key is None:
            return self.get_all_candidates()

        length = self._length(length)

        min_err = 999999
        candidates = []
        for l in length:
            X, Y = self.base[l]

            idx = bisect.bisect_left(Y, key)
            begin = max(0, idx - 1)
            end = min(idx + 2, len(X))

            for idx in range(begin, end):
                err = abs(Y[idx] - key)
                if abs(err - min_err) < 1e-9:
                    candidates.extend(X[idx])
                elif err < min_err:
                    candidates = copy.deepcopy(X[idx])
                    min_err = err
        return candidates

    def get_all_candidates(self):
        return sum([sum(D[0], []) for D in self.base.values()], [])

    def __len__(self):
        return sum([sum(len(x) for x in D[0]) for D in self.base.values()])

if __name__ == "__main__":
    # With ground KB
    kb = add_KB(kb_max_len = 5)
    print('len(kb):', len(kb))
    res = kb.get_candidates(0)
    print(res)
    res = kb.get_candidates(18, length = 2)
    print(res)
    res = kb.get_candidates(18, length = 8)
    print(res)
    res = kb.get_candidates(7, length = 3)
    print(res)
    print()
    
    # Without ground KB
    kb = add_KB()
    print('len(kb):', len(kb))
    res = kb.get_candidates(0)
    print(res)
    res = kb.get_candidates(18, length = 2)
    print(res)
    res = kb.get_candidates(18, length = 8)
    print(res)
    res = kb.get_candidates(7, length = 3)
    print(res)
    print()
    
    kb = hwf_KB(kb_max_len = 5)
    print('len(kb):', len(kb))
    res = kb.get_candidates(1, length = 3)
    print(res)
    res = kb.get_candidates(3.67, length = 5)
    print(res)
    print()
    
    
    # X = ["1+1", "0+1", "1+0", "2+0", "1+0+1"]
    # Y = [2, 1, 1, 2, 2]
    # kb = ClsKB(X, Y)
    # print('len(kb):', len(kb))
    # res = kb.get_candidates(2, 5)
    # print(res)
    # res = kb.get_candidates(2, 3)
    # print(res)
    # res = kb.get_candidates(None)
    # print(res)
    # print()
    
    # X = ["1+1", "0+1", "1+0", "2+0", "1+0.5", "0.75+0.75"]
    # Y = [2, 1, 1, 2, 1.5, 1.5]
    # kb = RegKB(X, Y)
    # print('len(kb):', len(kb))
    # res = kb.get_candidates(1.6)
    # print(res)
    # res = kb.get_candidates(1.6, length = 9)
    # print(res)
    # res = kb.get_candidates(None)
    # print(res)

