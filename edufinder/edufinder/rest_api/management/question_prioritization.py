from edufinder.rest_api.models import UserAnswer, Answer, AnswerChoice, Question, Education
import pandas as pd
import numpy as np
from math import log, e
from django.core.cache import cache

def get_question_tree():
    tree = cache.get('tree')

    if tree is None:
        dataset = fetch_data()
        if dataset is None:
            return
        questions = dataset.columns.tolist()[:-1]
        tree = create_branch(dataset, questions)
    return tree

def create_branch(dataset, questions):
    left = len(questions)
    dataCount = len(dataset.index)
    if left == 0 or dataCount == 0:
        return None

    question = find_local_best_question(dataset, questions)

    node = Node(question)

    questions.remove(question)
    for choice in AnswerChoice:
        newDataSet = get_where(dataset, question, choice)

        child = create_branch(newDataSet, questions.copy())

        if child is not None:
            node.add_child(child, choice)
    return node


def calculate_entropy(dataset):
    proportion = get_proportion(dataset, 'Decision')

    n_classes = np.count_nonzero(proportion)
    if n_classes <= 1:
        return 0

    ent = 0
    
    for i in proportion:
        ent -= i * log(i, 2)

    return ent


def calculate_gain(dataset, question_id, dataset_entropy):
    sum = 0
    probs = get_proportion(dataset, question_id)
    
    for choice in AnswerChoice:
        try:
            sum += probs[choice] * calculate_entropy(dataset[dataset[question_id] == choice])
        except KeyError:
            continue
    
    return  dataset_entropy - sum


def get_proportion(dataset, column):
    n_labels = len(dataset.index)
    counts = dataset[column].value_counts()
    probs = counts / n_labels
    return pd.Series(probs)

def fetch_data():
    userAnswers = UserAnswer.objects.all()

    if not userAnswers:
        return

    df = pd.DataFrame()

    for user in userAnswers:
        data = {'Decision': str(user.education.pk)}
        for answer in user.answer_set.all():
            data[answer.question.pk] = answer.answer
        pseries = pd.Series(data)
        df = df.append(pseries, ignore_index=True)
        
    dec_column = df.pop("Decision")
    df = df.reindex(sorted(df.columns, key=int), axis=1)
    df.insert(len(df.columns), "Decision", dec_column)
    return df


def find_local_best_question(dataset, questions):
    dataset_entropy = calculate_entropy(dataset)

    bestQuestion = questions[0]
    bestGain = calculate_gain(dataset, questions[0], dataset_entropy)
    for i in range(1, len(questions)):
        gain = calculate_gain(dataset, questions[i], dataset_entropy)
        if gain < bestGain:
            bestQuestion = questions[i]
            bestGain = gain

    return bestQuestion
    

def get_where(dataset, question, choice):
    return dataset[dataset[question] == choice]


class Node:
    "Generic tree node."
    def __init__(self, question):
        self.question = question
        self.children = dict()
    def __repr__(self):
        return self.question.question  

    def print_tree(self, choice, prefix = ""):
        if self.parent is not None:
            print(f'{prefix}{choice} -- {self.question.question}')
        else:
            print(prefix + self.question.question)

        for choice, child in self.children.items():
            child.print_tree(choice, prefix = prefix+"--")

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, node, choice):
        assert isinstance(node, Node)
        self.children[choice] = node
        node.parent = self
