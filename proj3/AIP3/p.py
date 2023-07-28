#!/usr/bin/python3.9
import nltk
from nltk.util import ngrams
from collections import Counter


path_test_set  = ["./AI_P3/test_set/test_file.txt"]
path_train_set = ["./AI_P3/train_set/ferdowsi_train.txt",
                  "./AI_P3/train_set/hafez_train.txt",
                  "./AI_P3/train_set/molavi_train.txt"
]

Lambda  = [0.86, 0.13, 0.01]
### Epsilon = None # no need

remove_lower = 2
debug = False

class poet:
    def __init__(self, train_path):
        self.train_path = train_path
        self.epsilon = 1
        self.unigram = self.cal_unigram()
        self.bigram  = self.cal_bigram()
        # self.backoff = self.cal_backoff(self.cal_bigram(), self.unigram)

    def cal_unigram(self):
        f = open(self.train_path, 'r')
        sentences = []
        while True:
            r = f.readline()
            if r == '':
                break
            sentences.append(r[:-1])

        dic = {}
        for s in sentences:
            new_values = dict(Counter(ngrams(nltk.word_tokenize(s), 1)))
            for k in new_values.keys():
                if dic.get(k) == None:
                    dic[k] = new_values[k]
                else:
                    dic[k] = dic[k] + new_values[k]

        f.close()
        new_dic = {}
        sum_of_values = 0
        for k in dic.keys():
            if dic.get(k) > remove_lower:
                new_dic[k[0]] = dic[k]
                sum_of_values = sum_of_values + new_dic[k[0]]

        for k in new_dic.keys():
            new_dic[k] = new_dic[k] / sum_of_values

        return new_dic

    def cal_bigram(self):
        f = open(self.train_path, 'r')
        sentences = []
        while True:
            r = f.readline()
            if r == '':
                break
            sentences.append(r[:-1])

        dic = {}
        # sum_of_all_values = 0
        for s in sentences:
            new_values = dict(Counter(ngrams(nltk.word_tokenize(s), 2)))
            for k in new_values.keys():
                if dic.get(k) == None:
                    dic[k] = new_values[k]
                else:
                    dic[k] = dic[k] + new_values[k]
                # sum_of_all_values = sum_of_all_values + dic[k]                    

        f.close()
        new_dic = {}
        sum_of_values = 0
        for k in dic.keys():
            if dic.get(k) > remove_lower:
                new_dic[k] = dic[k]
                sum_of_values = sum_of_values + new_dic[k]
                    
        for k in new_dic.keys():
            new_dic[k] = new_dic[k] / sum_of_values
            if self.epsilon > new_dic[k]:
                self.epsilon = new_dic[k]
        print(self.train_path[18:self.train_path.rfind('_')] + " epsilon = " + str(self.epsilon))

        return new_dic

    def cal_possibility(self, sentence):
        b = dict(Counter(ngrams(nltk.word_tokenize(sentence), 2)))
        # print(b)
        p = 1
        for k in b.keys():
            bi = self.bigram.get(k)
            un = self.unigram.get(k[1])

            if bi == None:
                bi = 0
            if un == None:
                un = 0

            p = p * (Lambda[0] * bi + Lambda[1] * un + Lambda[2] * self.epsilon)
            # if self.backoff.get(k) != None:
            #     p = p * self.backoff[k]
            # else:
            #     if self.unigram.get(k[1]) != None:
            #         p = p * self.unigram[k[1]]
            #     p = p * self.epsilon * Lambda[2]
        return p


class Result:
    def __init__(self, result, Lambda, poets_dic):
        self.result = result
        self.Lambda = Lambda
        self.poets_dic = poets_dic

    def p(self):
        return ("\nlambda = " + str(self.Lambda) +
                "\nresult  : " + str(self.result) +
                "\nferdowsi: " + str(poets_dic["ferdowsi"] / 1000) +
                "\nhafez   : " + str(poets_dic["hafez"] / 684) +
                "\nmolavi  : " + str(poets_dic["molavi"] / 1068) + "\n")



if __name__ == "__main__":
    ferdowsi = poet(path_train_set[0])
    hafez    = poet(path_train_set[1])
    molavi   = poet(path_train_set[2])
    poets = ["ferdowsi", "hafez", "molavi"]


    test_dic = {}
    f = open(path_test_set[0], 'r')
    while True:
        sentence = f.readline()
        if sentence == '':
            f.close()
            break
        test_dic[sentence[2:-1]] = int(sentence[0])
        sentence = sentence[2:-1]
    f.close()

    true_positive = 0
    poets_dic = {
                "ferdowsi": 0,
                "hafez"   : 0,
                "molavi"  : 0
    }

    for sentence in test_dic.keys():
        f_possibility = ferdowsi.cal_possibility(sentence)
        h_possibility = hafez.cal_possibility(sentence)
        m_possibility = molavi.cal_possibility(sentence)

        most_possibility = "ferdowsi"
        if  h_possibility > f_possibility:
            most_possibility = "hafez"
            if m_possibility > h_possibility:
                most_possibility = "molavi"
        elif m_possibility > f_possibility:
            most_possibility = "molavi"

        # print(most_possibility)
        if test_dic[sentence] == poets.index(most_possibility) + 1:
            true_positive = true_positive + 1
            poets_dic[most_possibility] = poets_dic[most_possibility] + 1

    print("\n\nresult = " + str(true_positive / test_dic.__len__() *100) + "%")
    # print(  "\nlambda = " + str(Lambda) +
    #         "\nresult  : " + str(true_positive / test_dic.__len__() *100) +
    print(  "\nferdowsi: " + str(poets_dic["ferdowsi"] / 1000) +
            "\nhafez   : " + str(poets_dic["hafez"] / 684) +
            "\nmolavi  : " + str(poets_dic["molavi"] / 1068) + "\n"
    )


