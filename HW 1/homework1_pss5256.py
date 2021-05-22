############################################################
# CMPSC 442: Homework 1
############################################################

student_name = "Param S. Somane"


############################################################
# Section 1: Working with Lists
############################################################

def extract_and_apply(l, p, f):
    return [f(x) for x in l if p(x)]


def concatenate(seqs):
    return [x for y in seqs for x in y]


def transpose(matrix):
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]


############################################################
# Section 2: Sequence Slicing
############################################################

def copy(seq):
    return seq[:]


def all_but_last(seq):
    return seq[:-1]


def every_other(seq):
    return seq[::2]


############################################################
# Section 3: Combinatorial Algorithms
############################################################

def prefixes(seq):
    for i in range(len(seq) + 1):
        yield seq[:i]


def suffixes(seq):
    for i in range(len(seq) + 1):
        yield seq[i:]


def slices(seq):
    for i in range(len(seq)):
        for j in range(i, len(seq)):
            yield seq[i:j + 1]


############################################################
# Section 4: Text Processing
############################################################

def normalize(text):
    text = text.strip(' ').split(' ')
    answer = text[0]
    for i in range(1, len(text)):
        if text[i] != '':
            answer = answer + ' ' + text[i]
    return answer.lower()


def no_vowels(text):
    vowels = ['a', 'A', 'e', 'E', 'i', 'I', 'o', 'O', 'u', 'U']
    answer = ''
    for i in range(0, len(text)):
        try:
            vowels.index(text[i])
        except ValueError:
            answer = answer + text[i]
    return answer


def digits_to_words(text):
    num_dic = {'0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four', '5': 'five', '6': 'six', '7': 'seven',
               '8': 'eight', '9': 'nine'}
    answer = ''
    for x in text:
        if x.isdigit():
            answer = answer + num_dic[x] + ' '
    return answer.strip(' ')


def to_mixed_case(name):
    name = name.strip('_').split('_')
    answer = name[0].lower()
    for i in range(1, len(name)):
        if name[i] != '':
            answer = answer + name[i].capitalize()
    return answer


############################################################
# Section 5: Polynomials
############################################################

class Polynomial(object):

    def __init__(self, polynomial):
        self.polynomial = tuple(polynomial)

    def get_polynomial(self):
        return self.polynomial

    def __neg__(self):
        return Polynomial([(-x, y) for (x, y) in self.polynomial])

    def __add__(self, other):
        return Polynomial(self.polynomial + other.polynomial)

    def __sub__(self, other):
        other = -other
        return Polynomial(self.polynomial + other.polynomial)

    def __mul__(self, other):
        return Polynomial([(a * b, n + m) for (a, n) in self.polynomial for (b, m) in other.polynomial])

    def __call__(self, x):
        return sum(a * x ** n for (a, n) in self.polynomial)

    def simplify(self):
        max_index = 0
        for (a, n) in self.polynomial:
            if n > max_index:
                max_index = n
        coefficients = [0] * (max_index + 1)
        for (a, n) in self.polynomial:
            coefficients[n] += a
        simplified_polynomial = []
        for n in reversed(range(max_index + 1)):
            if coefficients[n] != 0:
                simplified_polynomial.append((coefficients[n], n))
        self.polynomial = tuple([(0, 0)] if simplified_polynomial == [] else simplified_polynomial)

    @staticmethod
    def variable_portion(index):
        if index == 0:
            return ''
        elif index == 1:
            return 'x'
        return 'x^' + str(index)

    def __str__(self):
        (a, n) = self.polynomial[0]
        string = ('-' if a < 0 else '') + (str(abs(a)) if abs(a) != 1 or n == 0 else '') + self.variable_portion(n)
        for i in range(1, len(self.polynomial)):
            (a, n) = self.polynomial[i]
            string = string + ' ' + ('+' if a >= 0 else '-') + ' ' + (
                str(abs(a)) if abs(a) != 1 or n == 0 else '') + self.variable_portion(n)
        return string
