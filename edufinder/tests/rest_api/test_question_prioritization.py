from django.test import TestCase
from edufinder.rest_api.management.question_prioritization import *
from .test_base import TestBase
import pandas as pd
import numpy as np
from django.core.cache import cache

class QuestionPrioritizationTest(TestBase):

    def setUp(self):
        self.dataset = pd.DataFrame({'A': pd.Series([1, 2, -1, np.nan, 2, 1, 2]),
                                'B': pd.Series([1, 2, 0, -2, np.nan, -2, 1]),
                                'Decision': pd.Series([10, 10, 20, 20, 30, 30, 30])})

    def test_get_proportions(self):
        proportions = get_proportions(self.dataset, 'A')

        self.assertEqual(round(proportions[1], 2), 0.29)
        self.assertEqual(round(proportions[2], 2), 0.43)
        self.assertEqual(round(proportions[-1], 2), 0.14)

    def test_calculate_entropy(self):
        proportions = get_proportions(self.dataset, 'A')

        ent = calculate_entropy(self.dataset[self.dataset['A'] == 2])
        
        self.assertEqual(round(ent, 2), 0.92)

    def test_calculate_gain(self):
        dataset_entropy = calculate_entropy(self.dataset)

        gainA = calculate_gain(self.dataset, 'A', dataset_entropy)
        gainB = calculate_gain(self.dataset, 'B', dataset_entropy)
        
        self.assertEqual(round(gainA, 3), 0.877)
        self.assertEqual(round(gainB, 3), 0.985)

    def test_tree_is_saved(self):
        self.create_user_answer()

        get_question_tree()
        tree = cache.get('question_tree')

        self.assertIsNotNone(tree)

    def test_depth_is_13(self):
        self.create_user_answer()

        tree = get_question_tree()

        depth = 1
        while len(tree.children.values()) > 0:
            tree = list(tree.children.values())[0]
            depth += 1

        self.assertEqual(depth, 13)