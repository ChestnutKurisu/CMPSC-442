############################################################
# CMPSC 442: Homework 6
############################################################

student_name = "Param Somane"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
from collections import Counter
from collections import defaultdict

############################################################
# Section 1: Hidden Markov Models
############################################################


def load_corpus(path):
    return [[tuple(entry.split('=')) for entry in line.split()] for line in open(path, 'r', encoding="utf8")]


class Tagger(object):
    def __init__(self, sentences):
        self.tag_set = ['NOUN', 'VERB', 'ADJ', 'ADV', 'PRON', 'DET', 'ADP', 'NUM', 'CONJ', 'PRT', '.', 'X']
        transition_frequency = defaultdict(int)
        emission_frequency = defaultdict(int)
        for line in sentences:
            for i in range(len(line)):
                emission_frequency[(line[i][1], line[i][0])] += 1
            for i in range(len(line) - 1):
                transition_frequency[(line[i][1], line[i + 1][1])] += 1
        transitions = Counter(transition_frequency)
        emissions = Counter(emission_frequency)
        initial_tag_frequency = {tag: sum(1 for line in sentences if line[0][1] == tag) for tag in self.tag_set}
        tag_count = {tag: sum(1 for line in sentences for word, pos_tag in line if pos_tag == tag) for tag in self.tag_set}
        self.a = {(t_i, t_j): (transition_frequency[(t_i, t_j)] + 1e-5) / (tag_count.get(t_i, 0) + 1e-5 * transitions[t_j]) for (t_i, t_j) in transition_frequency.keys()}
        self.a.update({('X', w): 1e-5 / (tag_count.get(t, 0) + 1e-5 * transitions[t]) for (t, w) in transition_frequency.keys()})
        self.b = {(t, w): (emission_frequency[(t, w)] + 1e-5) / (tag_count.get(t, 0) + 1e-5 * emissions[t]) for (t, w) in emission_frequency}
        self.b.update({('X', w): 1e-5 / (tag_count.get(t, 0) + 1e-5 * emissions[t]) for (t, w) in emission_frequency.keys()})
        self.pi = {t: (initial_tag_frequency[t] + 1e-5) / (len(sentences) + 1e-5 * len(initial_tag_frequency)) for t in initial_tag_frequency.keys()}

    def most_probable_tags(self, tokens):
        return [max((self.b.get((tag, t), 0) if (tag, t) in self.b.keys() else self.b.get(("X", tag), 0),
                     tag if (tag, t) in self.b.keys() else 'X') for tag in self.tag_set)[1] for t in tokens]

    def viterbi_tags(self, tokens):
        alpha = [{tag: self.pi.get(tag, 0) * self.b.get((tag, tokens[0]), 0) for tag in self.tag_set}]
        alpha.extend([{} for i in range(len(tokens) - 1)])
        alpha_tag = [{} for i in range(len(tokens))]
        for t in range(len(tokens) - 1):
            for t_j in self.tag_set:
                (alpha[t + 1][t_j], alpha_tag[t + 1][t_j]) = max([(alpha[t][t_i] * self.a.get((t_i, t_j), 0) * self.b.get((t_j, tokens[t + 1]), 1 if t_j == "X" else 0), t_i) for t_i in self.tag_set])
        backtrace = [max([(tag, alpha[-1][tag]) for tag in self.tag_set], key=lambda x: x[1])[0]]
        backtrace.extend(alpha_tag[token][backtrace[-1]] for token in range(len(tokens) - 1, 0, -1))
        return list(reversed(backtrace))