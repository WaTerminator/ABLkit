# coding: utf-8
# ================================================================#
#   Copyright (C) 2020 Freecss All rights reserved.
#
#   File Name     ：models.py
#   Author        ：freecss
#   Email         ：karlfreecss@gmail.com
#   Created Date  ：2020/04/02
#   Description   ：
#
# ================================================================#
from itertools import chain

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

from sklearn.svm import LinearSVC

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from models.basic_model import BasicModel

import pickle as pk
import random

from sklearn.neighbors import KNeighborsClassifier
import numpy as np


def get_part_data(X, i):
    return list(map(lambda x: x[i], X))


def merge_data(X):
    ret_mark = list(map(lambda x: len(x), X))
    ret_X = list(chain(*X))
    return ret_X, ret_mark


def reshape_data(Y, marks):
    begin_mark = 0
    ret_Y = []
    for mark in marks:
        end_mark = begin_mark + mark
        ret_Y.append(Y[begin_mark:end_mark])
        begin_mark = end_mark
    return ret_Y


class WABLBasicModel:
    def __init__(self, base_model, pseudo_label_list):
        self.cls_list = []
        self.cls_list.append(base_model)

        self.pseudo_label_list = pseudo_label_list
        self.mapping = dict(zip(pseudo_label_list, list(range(len(pseudo_label_list)))))
        self.remapping = dict(
            zip(list(range(len(pseudo_label_list))), pseudo_label_list)
        )

    def predict(self, X):
        data_X, marks = merge_data(X)
        prob = self.cls_list[0].predict_proba(X=data_X)
        _cls = prob.argmax(axis=1)
        cls = list(map(lambda x: self.remapping[x], _cls))

        prob = reshape_data(prob, marks)
        cls = reshape_data(cls, marks)

        return {"cls": cls, "prob": prob}

    def valid(self, X, Y):
        data_X, _ = merge_data(X)
        _data_Y, _ = merge_data(Y)
        data_Y = list(map(lambda y: self.mapping[y], _data_Y))
        score = self.cls_list[0].score(X=data_X, y=data_Y)
        return score, [score]

    def train(self, X, Y):
        # self.label_lists = []
        data_X, _ = merge_data(X)
        _data_Y, _ = merge_data(Y)
        data_Y = list(map(lambda y: self.mapping[y], _data_Y))
        self.cls_list[0].fit(X=data_X, y=data_Y)


class DecisionTree(WABLBasicModel):
    def __init__(self, code_len, label_lists, share=False):
        self.code_len = code_len
        self._set_label_lists(label_lists)

        self.cls_list = []
        self.share = share
        if share:
            # 本质上是同一个分类器
            self.cls_list.append(
                DecisionTreeClassifier(random_state=0, min_samples_leaf=3)
            )
            self.cls_list = self.cls_list * self.code_len
        else:
            for _ in range(code_len):
                self.cls_list.append(
                    DecisionTreeClassifier(random_state=0, min_samples_leaf=3)
                )


class KNN(WABLBasicModel):
    def __init__(self, code_len, label_lists, share=False, k=3):
        self.code_len = code_len
        self._set_label_lists(label_lists)

        self.cls_list = []
        self.share = share
        if share:
            # 本质上是同一个分类器
            self.cls_list.append(KNeighborsClassifier(n_neighbors=k))
            self.cls_list = self.cls_list * self.code_len
        else:
            for _ in range(code_len):
                self.cls_list.append(KNeighborsClassifier(n_neighbors=k))


class CNN(WABLBasicModel):
    def __init__(self, base_model, code_len, label_lists, share=True):
        assert share == True, "Not implemented"

        label_lists = [sorted(list(set(label_list))) for label_list in label_lists]
        self.label_lists = label_lists

        self.code_len = code_len

        self.cls_list = []
        self.share = share
        if share:
            self.cls_list.append(base_model)

    def train(self, X, Y, n_epoch=100):
        # self.label_lists = []
        if self.share:
            # 因为是同一个分类器，所以只需要把数据放在一起，然后训练其中任意一个即可
            data_X, _ = merge_data(X)
            data_Y, _ = merge_data(Y)
            self.cls_list[0].fit(X=data_X, y=data_Y, n_epoch=n_epoch)
            # self.label_lists = [sorted(list(set(data_Y)))] * self.code_len
        else:
            for i in range(self.code_len):
                data_X = get_part_data(X, i)
                data_Y = get_part_data(Y, i)
                self.cls_list[i].fit(data_X, data_Y)
                # self.label_lists.append(sorted(list(set(data_Y))))


if __name__ == "__main__":
    # data_path = "utils/hamming_data/generated_data/hamming_7_3_0.20.pk"
    data_path = "datasets/generated_data/0_code_7_2_0.00.pk"
    codes, data, labels = pk.load(open(data_path, "rb"))

    cls = KNN(7, False, k=3)
    cls.train(data, labels)
    print(cls.valid(data, labels))
    for res in cls.predict_proba(data):
        print(res)
        break

    for res in cls.predict(data):
        print(res)
        break
    print("Trained")
