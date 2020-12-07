from edufinder.rest_api.models import UserAnswer, Answer, AnswerChoice, Question, Education
import pandas as pd
import numpy as np
from math import log, e
from django.core.cache import cache

MAX_DEPTH = 13

def get_question_tree():
    return cache.get('question_tree') or create_question_tree()

def create_question_tree():
    dataset = fetch_data()
    if dataset is None:
        return
    questions = dataset.columns.tolist()[:-1]
    tree = create_branch(dataset, questions)
    cache.set('question_tree', tree)
    return tree

def create_branch(dataset, questions, depth = 1):
    left = len(questions)
    data_count = len(dataset.index)
    if left == 0 or data_count == 0 or depth > MAX_DEPTH:
        return None

    question = find_local_best_question(dataset, questions)

    node = Node(question)

    questions.remove(question)

    # Iterate through the reduced answer choices 
    # -1 represents the negative answers, 0 represents "don't know" 
    # and 1 represents the postive answers 
    for choice in [-1,0,1]:
        new_data_set = get_where(dataset, question, choice)

        child = create_branch(new_data_set, questions.copy(), depth+1)

        if child:
            node.add_child(child, choice)
    return node


def calculate_entropy(dataset):
    proportion = get_proportions(dataset, 'Decision')

    n_classes = np.count_nonzero(proportion)
    if n_classes <= 1:
        return 0

    ent = 0
    
    for i in proportion:
        ent -= i * log(i, 2)

    return ent


def calculate_gain(dataset, question_id, dataset_entropy):
    sum = 0
    probs = get_proportions(dataset, question_id)

    for choice in AnswerChoice:
        try:
            sum += probs[choice] * calculate_entropy(dataset[dataset[question_id] == choice])
        except KeyError:
            continue
    
    return  dataset_entropy - sum


def get_proportions(dataset, column):
    n_labels = len(dataset.index)

    # Get list with amounts of each unique item in the column
    counts = dataset[column].value_counts()

    # Get proportion of each item
    probs = counts / n_labels
    return pd.Series(probs)

def fetch_data():
    user_answers = UserAnswer.objects.all()

    if not user_answers:
        return

    df = pd.DataFrame()

    for user in user_answers:
        data = {'Decision': str(user.education.pk)}
        for answer in user.answer_set.all():
            # Reduce the 5 possible choices to 3: (-1, 0 and 1) 
            data[answer.question.pk] = np.sign(answer.answer)
        pseries = pd.Series(data)
        df = df.append(pseries, ignore_index=True)
        
    dec_column = df.pop("Decision")
    df = df.reindex(sorted(df.columns, key=int), axis=1)
    df.insert(len(df.columns), "Decision", dec_column)
    return df


def find_local_best_question(dataset, questions):
    dataset_entropy = calculate_entropy(dataset)

    best_question = questions[0]
    best_gain = calculate_gain(dataset, questions[0], dataset_entropy)
    for i in range(1, len(questions)):
        gain = calculate_gain(dataset, questions[i], dataset_entropy)
        if gain < best_gain:
            best_question = questions[i]
            best_gain = gain

    return best_question
    

def get_where(dataset, question, choice):
    return dataset[dataset[question] == choice]


class Node:
    "Generic tree node."
    def __init__(self, question):
        self.question = question
        self.children = dict()
        self.parent = None

    def add_child(self, node, choice):
        self.children[choice] = node
        node.parent = self
