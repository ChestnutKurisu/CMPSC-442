############################################################
# CMPSC442: Homework 5
############################################################

student_name = "Param Somane"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import email
import math
import os


############################################################
# Section 1: Spam Filter
############################################################

def load_tokens(email_path):
    tokens = []
    file_contents = open(email_path, "r", encoding="utf8")
    message_obj = email.message_from_file(file_contents)
    for line in email.iterators.body_line_iterator(message_obj):
        tokens.extend(line.strip().split())
    return tokens


def log_probs(email_paths, smoothing):
    count = {}
    sum_count = 0
    for i in range(0, len(email_paths)):
        V_i = load_tokens(email_paths[i])
        for w in V_i:
            count[w] = (1 if w not in count.keys() else count[w] + 1)
        sum_count += len(V_i)
    V = len(count)
    P = {w: math.log((count[w] + smoothing) / (sum_count + smoothing * (V + 1))) for w in count.keys()}
    P["<UNK>"] = math.log(smoothing / (sum_count + smoothing * (V + 1)))
    return P


class SpamFilter(object):

    def __init__(self, spam_dir, ham_dir, smoothing):
        spam_dic = ["{0}/{1}".format(spam_dir, email) for email in os.listdir(spam_dir)]
        ham_dic = ["{0}/{1}".format(ham_dir, email) for email in os.listdir(ham_dir)]
        # ham = not spam
        self.P = {}
        self.P["spam"] = len(spam_dic) / (len(spam_dic) + len(ham_dic))
        self.P["not spam"] = 1 - self.P["spam"]
        self.log_P_spam = log_probs(spam_dic, smoothing)
        self.log_P_ham = log_probs(ham_dic, smoothing)

    def is_spam(self, email_path):
        V = load_tokens(email_path)
        P_spam = math.log(self.P["spam"])
        P_ham = math.log(self.P["not spam"])
        for w in V:
            P_spam += self.log_P_spam[w] if w in self.log_P_spam.keys() else self.log_P_spam["<UNK>"]
            P_ham += self.log_P_ham[w] if w in self.log_P_ham.keys() else self.log_P_ham["<UNK>"]
        return P_spam >= P_ham

    def most_indicative_spam(self, n):
        return list(list(
            zip(*reversed(sorted([(self.log_P_spam[w] - math.log((math.exp(self.log_P_spam[w]) * self.P["spam"]) + (
                    math.exp(self.log_P_ham[w]) * self.P["not spam"])), w) for w in self.log_P_spam.keys() if
                                  w in self.log_P_ham and w != "<UNK>"])[-n:])))[1])

    def most_indicative_ham(self, n):
        return list(list(
            zip(*reversed(sorted([(self.log_P_ham[w] - math.log(((math.exp(self.log_P_spam[w]) * self.P["spam"]) + (
                    math.exp(self.log_P_ham[w]) * self.P["not spam"]))), w) for w in self.log_P_ham if
                                  w in self.log_P_spam.keys() and w != "<UNK>"])[-n:])))[1])
