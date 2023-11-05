from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)

DB_CONFIG = {
    'host' : "54.210.73.216",
    'user' : "pknadimp",
    'password' : "1234",
    'database' : "Money"
}

class Database:
    def __enter__(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


@app.route("/register_user", methods=['POST'])
def register_user():
    user_data = request.json
    
    if not ('username' in user_data and 'personality_data' in user_data and 'avatar_url' in user_data):
        return jsonify({"error": "Lacking name, personality data, and/or avatar_url"}), 400

    username = user_data['username']
    personality_data = user_data['personality_data']
    avatar_url = user_data['avatar_url']

    with Database() as cursor:
        # Check if the username already exists
        check_query = "SELECT 1 FROM Money.Users WHERE username = %s"
        cursor.execute(check_query, (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({"error": "Username already exists."}), 409  

        # Prepare the SQL query to insert a new user with personality data and avatar URL
        insert_query = "INSERT INTO Money.Users (username, personality_data, avatar_url, last_streak) VALUES (%s, %s, %s, NOW())"
        cursor.execute(insert_query, (username, personality_data, avatar_url))

    return jsonify({"success": True, "message": "User registered successfully."}), 201

@app.route("/retrieve_user_data/<string:username>", methods=['GET'])
def retrieve_user_data(username):
    if not username:
        return jsonify({"error": "Username is required."}), 400

    with Database() as cursor:
        user_id_query = "SELECT user_id FROM Users WHERE username = %s"
        cursor.execute(user_id_query, (username,))
        user_id_result = cursor.fetchone()

        if not user_id_result:
            return jsonify({"error": "User not found."}), 404

        user_id = user_id_result[0]

        random_challenge_query = """
        SELECT challenge FROM Challenges 
        WHERE user_id = %s ORDER BY RAND() LIMIT 1
        """
        cursor.execute(random_challenge_query, (user_id,))
        random_challenge_result = cursor.fetchone()

        if not random_challenge_result:
            return jsonify({"error": "No challenges found for user."}), 404

        curr_challenge = random_challenge_result[0]

        update_curr_challenge_query = """
        UPDATE Users SET curr_challenge = %s 
        WHERE user_id = %s
        """
        cursor.execute(update_curr_challenge_query, (curr_challenge, user_id))
    
    with Database() as cursor:

        select_query = """
        SELECT user_id, streak_count, avatar_tier, curr_challenge, avatar_url 
        FROM Users 
        WHERE username = %s
        """
        cursor.execute(select_query, (username,))
        user_data = cursor.fetchone()

        if user_data:
            response = {
                "user_id": user_data[0],
                "streak_count": user_data[1],
                "avatar_tier": user_data[2],
                "curr_challenge": user_data[3],
                "avatar_url": user_data[4]
            }
            return jsonify(response), 200
        else:
            return jsonify({"error": "Error retrieving updated user data."}), 500



@app.route("/update_personality/<string:username>", methods=['POST'])
def update_personality(username):
    # Get data from the JSON body of the request
    user_data = request.json
    personality_data = user_data.get("personality_data")

    # Ensure personality_data is present
    if not personality_data:
        return jsonify({"error": "Personality data is required."}), 400

    with Database() as cursor:
        # Check if the user exists by username
        cursor.execute("SELECT 1 FROM Users WHERE username = %s", (username,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            return jsonify({"error": "User not found."}), 404

        # Since the user exists, proceed with the update
        update_query = """
        UPDATE Users 
        SET personality_data = %s 
        WHERE username = %s
        """
        cursor.execute(update_query, (personality_data, username))

        # Ensure the update was successful
        if cursor.rowcount == 0:
            # No rows updated, handle the situation as you see fit
            return jsonify({"error": "No changes were made. Likely duplicated data."}), 500

        return jsonify({"success": True, "message": "Personality updated successfully."}), 200



if __name__ == "__main__":
    print("Host:", os.getenv("HOST"))
    print("User:", os.getenv("USER"))
    app.run(debug=True)


        
        