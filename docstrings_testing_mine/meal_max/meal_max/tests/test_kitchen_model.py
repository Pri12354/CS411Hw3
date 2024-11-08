import unittest
from unittest import mock
from meal_max.models.kitchen_model import (
    create_meal,
    delete_meal,
    get_leaderboard,
    get_meal_by_id,
    get_meal_by_name,
    update_meal_stats
    )
from meal_max.utils.sql_utils import get_db_connection
from meal_max.models.kitchen_model import Meal
import sqlite3

class TestKitchenModel(unittest.TestCase):
    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_create_meal_valid(self, mock_get_db_connection):
        # Set up a mock cursor and connection
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        
        # Call the function to create a meal
        create_meal("Pizza", "Italian", 15.0, "LOW")
        
        # Expected SQL and parameters
        expected_query = "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)"
        expected_params = ("Pizza", "Italian", 15.0, "LOW")

        # Retrieve actual SQL call and parameters
        actual_query = mock_cursor.execute.call_args[0][0]
        actual_params = mock_cursor.execute.call_args[0][1]

        # Debugging output to check the exact values
        print("Expected Query:", expected_query)
        print("Actual Query:", actual_query)
        print("Expected Parameters:", expected_params)
        print("Actual Parameters:", actual_params)

        # Normalize the queries and compare
        self.assertEqual(" ".join(expected_query.split()), " ".join(actual_query.split()))
        self.assertEqual(expected_params, actual_params)


    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_create_meal_invalid_difficulty(self, mock_get_db_connection):
        # Test for invalid difficulty level
        with self.assertRaises(ValueError):
            create_meal("Pizza", "Italian", 15.0, "INVALID")

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_create_meal_invalid_price(self, mock_get_db_connection):
        # Test for invalid price
        with self.assertRaises(ValueError):
            create_meal("Pizza", "Italian", -15.0, "LOW")

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_delete_meal_success(self, mock_get_db_connection):
        # Mocking the cursor and the database response
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (False,)  # Simulating meal is not deleted
        
        # Assume ID 1 exists and is not deleted
        delete_meal(1)
        
        # Ensure that the delete query was executed
        mock_cursor.execute.assert_called_with("UPDATE meals SET deleted = TRUE WHERE id = ?", (1,))

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_delete_meal_not_found(self, mock_get_db_connection):
        # Test for deleting a non-existing meal
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate meal not found
        
        with self.assertRaises(ValueError):
            delete_meal(1)
        
    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_leaderboard_single_entry(self, mock_get_db_connection):
        # Mocking the cursor to return a fake leaderboard
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Pizza", "Italian", 15.0, "LOW", 10, 6, 0.6)
        ]
        
        leaderboard = get_leaderboard()
        
        # Ensure that the correct meal data is returned
        self.assertEqual(len(leaderboard), 1)
        self.assertEqual(leaderboard[0]['meal'], "Pizza")
        self.assertEqual(leaderboard[0]['wins'], 6)

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_meal_by_id(self, mock_get_db_connection):
        # Mocking the cursor to return a meal by ID
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 15.0, "LOW", False)
        
        meal = get_meal_by_id(1)
        
        # Ensure that the meal is returned correctly
        self.assertEqual(meal.id, 1)
        self.assertEqual(meal.meal, "Pizza")

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_meal_by_id_not_found(self, mock_get_db_connection):
        # Test for when meal is not found by ID
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate meal not found
        
        with self.assertRaises(ValueError):
            get_meal_by_id(1)

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_meal_by_name(self, mock_get_db_connection):
        # Mocking the cursor to return a meal by name
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, "Pizza", "Italian", 15.0, "LOW", False)
        
        meal = get_meal_by_name("Pizza")
        
        # Ensure that the meal is returned correctly
        self.assertEqual(meal.id, 1)
        self.assertEqual(meal.meal, "Pizza")

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_meal_by_name_not_found(self, mock_get_db_connection):
        # Test for when meal is not found by name
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate meal not found
        
        with self.assertRaises(ValueError):
            get_meal_by_name("Pizza")

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_update_meal_stats_win(self, mock_get_db_connection):
        # Test for updating meal stats with a win
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (False,)  # Simulate meal is not deleted
        
        update_meal_stats(1, "win")
        
        # Ensure that the update query for a win was executed
        mock_cursor.execute.assert_any_call("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,))

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_update_meal_stats_loss(self, mock_get_db_connection):
        # Test for updating meal stats with a loss
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (False,)  # Simulate meal is not deleted
        
        update_meal_stats(1, "loss")
        
        # Ensure that the update query for a loss was executed
        mock_cursor.execute.assert_any_call("UPDATE meals SET battles = battles + 1 WHERE id = ?", (1,))

    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_update_meal_stats_invalid_result(self, mock_get_db_connection):
        # Test for invalid result in update stats
        with self.assertRaises(ValueError):
            update_meal_stats(1, "invalid_result")
    
    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_leaderboard_multiple_entries(self, mock_get_db_connection):
        # Mocking the database cursor and sample data
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Pizza", "Italian", 15.0, "LOW", 10, 6, 0.6),
            (2, "Burger", "American", 12.0, "MED", 8, 4, 0.5)
        ]
        
        # Call get_leaderboard and check results
        leaderboard = get_leaderboard(sort_by="wins")
        
        # Expected SQL query
        expected_query = """
            SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct 
            FROM meals WHERE deleted = false AND battles > 0 ORDER BY wins DESC
        """
        
        # Normalize SQL queries by removing extra whitespace and line breaks
        actual_query = mock_cursor.execute.call_args[0][0]
        self.assertEqual(" ".join(expected_query.split()), " ".join(actual_query.split()))

        # Verify returned leaderboard data
        self.assertEqual(len(leaderboard), 2)
        self.assertEqual(leaderboard[0]['meal'], "Pizza")
        self.assertEqual(leaderboard[0]['wins'], 6)


    @mock.patch('meal_max.models.kitchen_model.get_db_connection')
    def test_update_meal_stats(self, mock_get_db_connection):
        # Mocking the cursor for a meal that exists and is not deleted
        mock_cursor = mock.Mock()
        mock_get_db_connection.return_value.__enter__.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (False,)  # Meal is not deleted
        
        # Call update_meal_stats with a win
        update_meal_stats(1, "win")
        
        # Verify that the update query for a win was executed
        mock_cursor.execute.assert_any_call("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,))
        
        # Call update_meal_stats with a loss
        update_meal_stats(1, "loss")
        
        # Verify that the update query for a loss was executed
        mock_cursor.execute.assert_any_call("UPDATE meals SET battles = battles + 1 WHERE id = ?", (1,))

if __name__ == '__main__':
    unittest.main()

