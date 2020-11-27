from edufinder.rest_api.models import UserAnswer, Answer, AnswerChoice, Question, Education
import pandas as pd
import numpy as np
from math import log, e


def create_question_tree():
    dataset = fetch_data()
    questions = dataset.columns.tolist()[:-1]
    return create_branch(dataset, questions)


def create_branch(dataset, questions, nodeChoice = None):
    left = len(questions)
    dataCount = len(dataset.index)
    if left == 0 or dataCount == 0:
        return None

    question = find_local_best_question(dataset, questions)

    node = Node(question, nodeChoice)

    questions.remove(question)
    for choice in AnswerChoice:
        newDataSet = get_where(dataset, question, choice)

        child = create_branch(dataSet, questions.copy(), choice)

        if child is not None:
            node.add_child(child)
    return node


def calculate_entropy(dataset, column, proportion):
    n_classes = np.count_nonzero(proportion)
    
    if n_classes <= 1:
        return 0

    ent = 0
    
    for i in proportion:
        ent -= i * log(i, 2)

    return ent


def calculate_gain(dataset, question_id):
    sum = 0
    probs = get_proportion(dataset, question_id)
    
    for choice in AnswerChoice:
        try:
            sum += probs[choice]
        except KeyError:
            continue
    return sum * calculate_entropy(dataset, question_id, probs)


def get_proportion(dataset, column):
    n_labels = len(dataset.index)
    counts = dataset[column].value_counts()
    probs = counts / n_labels
    return pd.Series(probs)

def fetch_data():
    userAnswers = UserAnswer.objects.all()
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
    bestQuestion = questions[0]
    bestGain = calculate_gain(dataset, questions[0])
    for i in range(1, len(questions)):
        gain = calculate_gain(dataset, questions[i])
        if gain < bestGain:
            bestQuestion = questions[i]
            bestGain = gain

    return bestQuestion
    

def get_where(dataset, question, choice):
    return dataset[dataset[question] == choice]


class Node:
    "Generic tree node."
    def __init__(self, question, choice = None, children=None):
        self.question = question
        self.children = []
        self.choice = choice
        if children is not None:
            for child in children:
                self.add_child(child)
    def __repr__(self):
        return self.question.question  

    def print_tree(self, prefix = ""):
        if self.choice is not None:
            print(prefix+self.choice + " into " + self.question.question)
        else:
            print(prefix+"root" + self.question.question)

        if self.children is not None:
            for child in self.children:
                child.print_tree(prefix+"--")

    def add_child(self, node):
        assert isinstance(node, Node)
        self.children.append(node)
