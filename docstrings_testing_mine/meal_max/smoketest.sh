#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meals
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal, $cuisine, $price, $difficulty) to the database..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  
  echo "Response: $response" 

  if echo "$response" | grep -q '"status": "combatant added"'; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}


delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "meal deleted"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name: $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}

############################################################
#
# Battle
#
############################################################

battle_test() {
  echo "Initiating battle between two prepared meals..."
  response=$(curl -s -X GET "$BASE_URL/battle")

  if echo "$response" | grep -q '"status": "battle complete"'; then
    echo "Battle completed successfully!"
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Result JSON:"
      echo "$response" | jq .
    else
      winner=$(echo "$response" | jq -r '.winner')
      echo "Winner: $winner"
    fi
  else
    echo "Failed to initiate battle."
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "combatants cleared"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

get_combatants() {
  echo "Getting combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrive combatants."
    exit 1
  fi
}

prep_combatant() {
  meal_name=$1

  echo "Preparing combatant with meal name: $meal_name..."

  # Properly escape the meal_name to handle any special characters
  payload="{\"meal\": \"$meal_name\"}"

  # Send the POST request with the corrected payload
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" -d "$payload")

  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Combatant prepared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatant JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Response: $response" 
    echo "Failed to prepare combatant."
    exit 1
  fi
}


############################################################
#
# Leaderboard
#
############################################################

get_leaderboard() {
  echo "Getting meal leaderboard sorted by specified criteria..."

  # Set default sort parameter, can be overwritten by command line argument or other logic
  sort_by=${1:-wins}

  # Validate the sort_by parameter
  valid_params=("wins" "win_pct")
  if [[ ! " ${valid_params[@]} " =~ " ${sort_by} " ]]; then
    echo "Invalid sort_by parameter: $sort_by"
    exit 1
  fi

  # Send GET request with the sort parameter
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."

    # Optionally echo the full JSON response if the ECHO_JSON variable is set to true
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by $sort_by):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    echo "Response: $response"
    exit 1
  fi
}


# Health checks
check_health
check_db

# Meals
create_meal "Pizza" "Italian" 10 "MED"
create_meal "Sushi" "Japanese" 15 "HIGH"
create_meal "Burger" "American" 8 "LOW"
create_meal "Butter Chicken" "Inidan" 8 "LOW"

delete_meal_by_id 1
get_meal_by_id 2
get_meal_by_name "Sushi"

# Battle
prep_combatant "Burger"
prep_combatant "Butter Chicken"
get_combatants
battle_test
clear_combatants

# Leaderboard
get_leaderboard "wins"
get_leaderboard "win_pct"

echo "All smoketests completed successfully!"