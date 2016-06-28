import os
import math
import random
import unittest

import Orange
from orangecontrib.recommendation import UserItemBaselineLearner

import numpy as np
from sklearn.metrics import mean_squared_error

class TestUserItemBaseline(unittest.TestCase):

    # def test_UserItemBaseline_swap_columns(self):
    #     # Recommender
    #     learner = UserItemBaselineLearner(verbose=False)
    #
    #     # Dataset 1
    #     filename = os.path.abspath(
    #         os.path.join(os.path.dirname(__file__), '../datasets/ratings.tab'))
    #     data = Orange.data.Table(filename)
    #     recommender = learner(data)
    #     prediction = recommender.predict_items()
    #     y_pred1 = prediction[data.X[:, recommender.order[0]],
    #                          data.X[:, recommender.order[1]]]
    #
    #     # Dataset 2
    #     filename = os.path.abspath(
    #         os.path.join(os.path.dirname(__file__), '../datasets/ratings2.tab'))
    #     data = Orange.data.Table(filename)
    #     recommender = learner(data)
    #     prediction = recommender.predict_items()
    #     y_pred2 = prediction[data.X[:, recommender.order[0]],
    #                          data.X[:, recommender.order[1]]]
    #
    #     # Compare results
    #     np.testing.assert_array_equal(y_pred1, y_pred2)


    def test_UserAvg_correctness(self):

        # Load data
        data = Orange.data.Table('ratings.tab')

        # Train recommender
        learner = UserItemBaselineLearner(verbose=False)
        recommender = learner(data)

        # Set ground truth
        ground_truth_dItems = [0.02142857, 0.42142857, -0.46428571, 0.02142857,
                               0.1547619]
        ground_truth_dUsers = [0.07142857, 0.48809524, 0.07142857, 0.1547619,
                               0.1547619, -0.51190476, -0.57857143, 0.48809524]

        # Compare results
        np.testing.assert_array_almost_equal(recommender.bias['dItems'],
                                             ground_truth_dItems,
                                             decimal=2)
        np.testing.assert_array_almost_equal(recommender.bias['dUsers'],
                                             ground_truth_dUsers,
                                             decimal=2)
        self.assertAlmostEqual(recommender.global_average, 3.17857, places=2)


    def test_UserItemBaseline_predict_items(self):

        # Load data
        data = Orange.data.Table('ratings.tab')

        # Train recommender
        learner = UserItemBaselineLearner(verbose=True)
        recommender = learner(data)

        # Compute predictions 1
        prediction = recommender.predict_items(users=None, top=None)

        # Compute predictions 2 (Execute the other branch)
        num_users = min(recommender.shape[0], 5)
        num_items = min(recommender.shape[1], 5)
        setUsers = random.sample(range(recommender.shape[0]), num_users)
        prediction2 = recommender.predict_items(users=setUsers, top=num_items)

        # Check correctness 1
        len_u, len_i = prediction.shape
        self.assertEqual(len_u, recommender.shape[0])
        self.assertEqual(len_i, recommender.shape[1])

        # Check correctness 2
        len_u, len_i = prediction2.shape
        self.assertEqual(len_u, num_users)
        self.assertEqual(len_i, num_items)


    def test_UserItemBaseline_input_data(self):

        # Load data
        data = Orange.data.Table('ratings.tab')

        # Train recommender
        learner = UserItemBaselineLearner(verbose=False)
        recommender = learner(data)
        print(str(recommender) + ' trained')

        # Compute predictions
        y_pred = recommender(data)

        # Compute RMSE
        rmse = math.sqrt(mean_squared_error(data.Y, y_pred))
        print('-> RMSE (input data): %.3f' % rmse)

        # Check correctness
        self.assertGreaterEqual(rmse, 0)


    def test_UserItemBaseline_pairs(self):

        # Load data
        data = Orange.data.Table('ratings.tab')

        # Train recommender
        learner = UserItemBaselineLearner(verbose=False)
        recommender = learner(data)

        # Create indices to test
        sample_size = 10
        num_users, num_items = recommender.shape
        idx_users = np.random.randint(0, num_users, size=sample_size)
        idx_items = np.random.randint(0, num_items, size=sample_size)
        indices = np.column_stack((idx_users, idx_items))

        # Compute predictions
        y_pred = recommender(indices)
        print('-> Same number? (pairs): %r' % (len(y_pred) == sample_size))

        # Check correctness
        self.assertEqual(len(y_pred), sample_size)


    def test_UserItemBaseline_CV(self):
        from Orange.evaluation.testing import CrossValidation

        # Load data
        data = Orange.data.Table('ratings.tab')

        user_item_baseline = UserItemBaselineLearner(verbose=False)
        learners = [user_item_baseline]

        res = CrossValidation(data, learners, k=3)
        rmse = Orange.evaluation.RMSE(res)
        r2 = Orange.evaluation.R2(res)

        print("Learner  RMSE  R2")
        for i in range(len(learners)):
            print(
                "{:8s} {:.2f} {:5.2f}".format(learners[i].name, rmse[i], r2[i]))

        self.assertIsInstance(rmse, np.ndarray)

if __name__ == "__main__":
    #unittest.main()

    # Test single test
    suite = unittest.TestSuite()
    suite.addTest(TestUserItemBaseline("test_UserItemBaseline_input_data"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

