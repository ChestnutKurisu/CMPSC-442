############################################################
# CMPSC 442: Homework 4
############################################################

student_name = "Param Somane"

############################################################
# Imports
############################################################
import itertools


############################################################
# Section 1: Propositional Logic
############################################################

class Expr(object):
    def __hash__(self):
        return hash((type(self).__name__, self.hashable))


class Atom(Expr):
    def __hash__(self):
        return Expr.__hash__(self)

    def __init__(self, name):
        self.name = name
        self.hashable = name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name

    def __repr__(self):
        return "Atom(" + self.name + ")"

    def atom_names(self):
        return {self.name}

    def evaluate(self, assignment):
        return assignment[self.name]

    def to_cnf(self):
        return self


class Not(Expr):
    def __hash__(self):
        return Expr.__hash__(self)

    def __init__(self, arg):
        self.arg = arg
        self.hashable = arg

    def __eq__(self, other):
        return type(self) == type(other) and self.arg == other.arg

    def __repr__(self):
        return "Not(" + repr(self.arg) + ")"

    def atom_names(self):
        return self.arg.atom_names()

    def evaluate(self, assignment):
        return not self.arg.evaluate(assignment)

    def to_cnf(self):
        # Trivial cases where expression inside Not is a literal or its negation
        if type(self.arg.to_cnf()) == Atom:
            return Not(self.arg.to_cnf())
        if type(self.arg.to_cnf()) == Not:
            return self.arg.to_cnf().arg
        # De Morgan's laws
        if type(self.arg.to_cnf()) == Or:
            return And(*[Not(y).to_cnf() for y in self.arg.to_cnf().hashable]).to_cnf()
        if type(self.arg.to_cnf()) == And:
            return Or(*[Not(y).to_cnf() for y in self.arg.to_cnf().hashable]).to_cnf()
        # Note that conditional statement negation is dealt by converting self.arg to cnf first


class And(Expr):
    def __hash__(self):
        return Expr.__hash__(self)

    def __init__(self, *conjuncts):
        self.conjuncts = frozenset(conjuncts)
        self.hashable = self.conjuncts

    def __eq__(self, other):
        return self.conjuncts == other.conjuncts

    def __repr__(self):
        return "And(" + ", ".join([repr(arg) for arg in self.hashable]) + ")"

    def atom_names(self):
        return set().union(*[arg.atom_names() for arg in self.hashable])

    def evaluate(self, assignment):
        for arg in self.hashable:
            if not arg.evaluate(assignment):
                return False
        return True

    def to_cnf(self):
        # Strategy: convert all literals (atoms) in expr to cnf individually
        # and then combine all ANDs into a single AND statement. We use distributivity
        # of AND over OR and associativity of AND.
        expression = []
        for arg in [arg.to_cnf() for arg in self.hashable]:
            if type(arg) == And:
                for inner_arg in arg.hashable:
                    expression.append(inner_arg)
            else:
                expression.append(arg)
        return And(*expression)


class Or(Expr):
    def __hash__(self):
        return Expr.__hash__(self)

    def __init__(self, *disjuncts):
        self.disjuncts = frozenset(disjuncts)
        self.hashable = self.disjuncts

    def __eq__(self, other):
        return self.disjuncts == other.disjuncts

    def __repr__(self):
        return "Or(" + ", ".join([repr(arg) for arg in self.hashable]) + ")"

    def atom_names(self):
        return set().union(*[arg.atom_names() for arg in self.hashable])

    def evaluate(self, assignment):
        for arg in self.hashable:
            if arg.evaluate(assignment):
                return True
        return False

    def to_cnf(self):
        # Strategy: convert all literals (atoms) in expr to cnf individually
        # and then combine all ORs into a single OR statement. We use distributivity
        # of OR over AND and associativity of OR.
        expression = []
        for arg in [arg.to_cnf() for arg in self.hashable]:
            if type(arg) == Or:
                expression += [inner_arg for inner_arg in arg.hashable]
            else:
                expression.append(arg)
        or_form = Or(*expression)
        for disjunction in or_form.hashable:
            if type(disjunction) == And:
                new_or_list = list(set(or_form.hashable).difference({disjunction}))
                return And(
                    *[Or(*([d] + [arg for arg in new_or_list])).to_cnf() for d in list(disjunction.hashable)]).to_cnf()
        return Or(*expression)


class Implies(Expr):
    def __hash__(self):
        return Expr.__hash__(self)

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)

    def __eq__(self, other):
        return self.hashable == other.hashable

    def __repr__(self):
        return "Implies(" + repr(self.left) + ", " + repr(self.right) + ")"

    def atom_names(self):
        return set().union(*[arg.atom_names() for arg in self.hashable])

    def evaluate(self, assignment):
        return Or(Not(self.left), self.right).evaluate(assignment)

    def to_cnf(self):
        return Or(Not(self.left), self.right).to_cnf()


class Iff(Expr):
    def __hash__(self):
        return Expr.__hash__(self)

    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)

    def __eq__(self, other):
        return other.hashable == self.hashable or other.hashable == (self.right, self.left)

    def __repr__(self):
        return "Iff(" + repr(self.left) + ", " + repr(self.right) + ")"

    def atom_names(self):
        return set().union(*[arg.atom_names() for arg in self.hashable])

    def evaluate(self, assignment):
        return And(Implies(self.left, self.right), Implies(self.right, self.left)).evaluate(assignment)

    def to_cnf(self):
        return And(Implies(self.left, self.right), Implies(self.right, self.left)).to_cnf()


def satisfying_assignments(expr):
    atom_names = list(expr.atom_names())
    for n in range(2 ** len(atom_names)):
        binary_n = "{0:b}".format(n)
        binary_n = "0" * (len(atom_names) - len(binary_n)) + binary_n
        digit = 0
        assignment = {name: False for name in atom_names}
        for name in atom_names:
            assignment[name] = True if binary_n[digit] == '1' else False
            digit += 1
        if expr.evaluate(assignment):
            yield assignment


class KnowledgeBase(object):
    def __init__(self):
        self.internal_fact_set = set()

    def get_facts(self):
        return self.internal_fact_set

    def tell(self, expr):
        self.internal_fact_set.add(expr.to_cnf())

    def ask(self, expr):
        # Using resolution algorithm
        cnf = And(*self.get_facts(), Not(expr)).to_cnf()
        clauses = set()
        if type(cnf) == And:
            clauses = set(cnf.hashable)
        else:
            clauses = {cnf}
        new = set()
        # To improve efficiency by avoiding repeated iterations.
        checked_pairs = set()
        while True:
            clause_list = list(clauses)
            for (i, j) in set(itertools.product(set(range(len(clause_list))), set(range(len(clause_list))))).difference(
                    {(i, i) for i in range(len(clause_list))}):
                C_i = clause_list[i]
                C_j = clause_list[j]
                if (C_i, C_j) not in checked_pairs and (C_j, C_i) not in checked_pairs:
                    checked_pairs.add((C_i, C_j))
                    resolvents = set()
                    # PL-RESOLVE(C_i, C_j) (From Pg. 253)
                    if type(C_i) != Or:
                        C_i = Not(C_i).to_cnf()
                        if type(C_j) != Or:
                            if type(C_i) == type(C_j) and C_i == C_j:
                                return True
                        else:
                            if C_i in C_j.hashable:
                                resolvents = resolvents.union(C_j.hashable.difference({C_i}))
                    else:
                        if type(C_j) != Or:
                            C_j = Not(C_j).to_cnf()
                            if C_j in C_i.hashable:
                                resolvents = C_i.hashable.difference({C_j})
                        else:
                            intersect = C_j.hashable.intersection({Not(l_k).to_cnf() for l_k in C_i.hashable})
                            if len(intersect) == 1:
                                resolvents = C_i.hashable.difference({Not(next(iter(intersect))).to_cnf()}).union(
                                    C_j.hashable.difference(intersect))

                    if resolvents:
                        # Resolvents contains the empty clause
                        if len(resolvents) == 0:
                            return True
                        elif len(resolvents) == 1:
                            new.add(*resolvents)
                        else:
                            new.add(Or(*resolvents))
            if new.issubset(clauses):
                return False
            clauses = clauses.union(new)


############################################################
# Section 2: Logic Puzzles
############################################################

# Puzzle 1

# Populate the knowledge base using statements of the form kb1.tell(...)
kb1 = KnowledgeBase()
A, B, C, D, E = map(Atom, ["mythical", "mortal", "mammal", "horned", "magical"])
# If the unicorn is mythical, then it is immortal.
kb1.tell(Implies(A, Not(B)))
# If it is not mythical, then it is a mortal mammal.
kb1.tell(Implies(Not(A), And(B, C)))
# If the unicorn is either immortal or a mammal, then it is horned.
kb1.tell(Implies(Or(Not(B), C), D))
# The unicorn is magical if it is horned.
kb1.tell(Implies(D, E))

# Write an Expr for each query that should be asked of the knowledge base
mythical_query = A
magical_query = E
horned_query = D

# Queries made
# print(kb1.ask(mythical_query))
# print(kb1.ask(magical_query))
# print(kb1.ask(horned_query))

# Record your answers as True or False; if you wish to use the above queries,
# they should not be run when this file is loaded
is_mythical = False
is_magical = True
is_horned = True

# Puzzle 2
A = Atom("a")
J = Atom("j")
M = Atom("m")

# Write an Expr of the form And(...) encoding the constraints
party_constraints = And(Implies(Or(M, A), J), Implies(Not(M), A), Implies(A, Not(J)))

# Compute a list of the valid attendance scenarios using a call to
# satisfying_assignments(expr)
# print(list(satisfying_assignments(party_constraints)))
valid_scenarios = [{'a': False, 'j': True, 'm': True}]

# Write your answer to the question in the assignment
puzzle_2_question = """
The guests can attend without violating the constraints if and only if John and Mary
both come to the party but Ann does not come.
"""

# Puzzle 3

# Populate the knowledge base using statements of the form kb3.tell(...)
kb3 = KnowledgeBase()
room_one_prize = Atom("p1")
room_two_prize = Atom("p2")
room_one_empty = Atom("e1")
room_two_empty = Atom("e2")
sign_one_true = Atom("s1")
sign_two_true = Atom("s2")

# Each room may either contain a prize or be empty.
kb3.tell(Iff(room_one_prize, Not(room_one_empty)))
kb3.tell(Iff(room_two_prize, Not(room_two_empty)))
# The sign on the first door states: "This room contains a prize, and the other room is empty."
kb3.tell(Iff(sign_one_true, And(room_one_prize, room_two_empty)))
# The sign on the second door states: "At least one room contains a prize, and at least one room is empty."
# Since there are only two rooms, each of which can either have a prize or be empty, at least implies exactly here.
kb3.tell(Iff(sign_two_true, Or(And(room_one_prize, room_two_empty),
                               And(room_one_empty, room_two_prize))))
# Exactly one sign is true (XOR).
kb3.tell(And(Or(sign_one_true, sign_two_true), Or(Not(sign_one_true), Not(sign_two_true))))

# Queries made
# print(kb3.ask(room_one_prize))
# print(kb3.ask(room_two_prize))
# print(kb3.ask(room_one_empty))
# print(kb3.ask(room_two_empty))
# print(kb3.ask(sign_one_true))
# print(kb3.ask(sign_two_true))

# Write your answer to the question in the assignment; the queries you make
# should not be run when this file is loaded
puzzle_3_question = """
The sign on the first door is false while the sign on the second door is true. 
Thus, the prize is in the second room while the first room is empty.
"""

# Puzzle 4

# Populate the knowledge base using statements of the form kb4.tell(...)
kb4 = KnowledgeBase()
innocent_Adams = Atom("ia")
innocent_Brown = Atom("ib")
innocent_Clark = Atom("ic")
knew_Adams = Atom("ka")
knew_Brown = Atom("kb")
knew_Clark = Atom("kc")

# Adam: I didn’t do it. The victim was an old acquaintance of Brown’s. But Clark never knew him.
kb4.tell(Implies(innocent_Adams, And(knew_Brown, Not(knew_Clark))))
# Brown: I didn’t do it. I didn’t know the guy.
kb4.tell(Implies(innocent_Brown, Not(knew_Brown)))
# Clark: I didn’t do it. I saw both Adams and Brown downtown with the victim that day; one of them must have done it.
kb4.tell(Implies(innocent_Clark, And(knew_Adams, knew_Brown)))
# The two innocent men are telling the truth, but the guilty man is not.
kb4.tell(Or(And(innocent_Adams, innocent_Brown, Not(innocent_Clark)),
            And(innocent_Adams, Not(innocent_Brown), innocent_Clark),
            And(Not(innocent_Adams), innocent_Brown, innocent_Clark)))

# for query in [innocent_Adams, innocent_Brown, innocent_Clark, knew_Adams, knew_Brown, knew_Clark]:
#     print(kb4.ask(query))

# Uncomment the line corresponding to the guilty suspect
# guilty_suspect = "Adams"
guilty_suspect = "Brown"
# guilty_suspect = "Clark"

# Describe the queries you made to ascertain your findings
puzzle_4_question = """
I first populated the knowledge base with the claims made by Adams, Brown, and Clark and the assumption that the 
innocent suspects are being honest while the perpetrator is lying. I queried the knowledge base for the truths of 
innocent_Adams, innocent_Brown, and innocent_Clark. It turned out that the first and last of these were true and so 
Adams and Clark are innocent while Brown is guilty. Moreover, while both Adams and Brown knew the victim, 
Clark did not know the victim.
"""
