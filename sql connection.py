import mysql.connector
from mysql.connector import errorcode

# Establish the database connection
db_config = {
    'user': 'root',
    'password': 'sun',
    'host': 'localhost'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS music_streaming_service")
    cursor.execute("USE music_streaming_service")

    # Create tables
    TABLES = {}
    TABLES['users'] = (
        "CREATE TABLE IF NOT EXISTS users ("
        "  user_id INT AUTO_INCREMENT PRIMARY KEY,"
        "  username VARCHAR(50) NOT NULL UNIQUE,"
        "  password VARCHAR(255) NOT NULL"
        ")"
    )
    TABLES['songs'] = (
        "CREATE TABLE IF NOT EXISTS songs ("
        "  song_id INT AUTO_INCREMENT PRIMARY KEY,"
        "  title VARCHAR(100) NOT NULL,"
        "  artist VARCHAR(100),"
        "  album VARCHAR(100),"
        "  file_path VARCHAR(255) NOT NULL"
        ")"
    )
    TABLES['playlists'] = (
        "CREATE TABLE IF NOT EXISTS playlists ("
        "  playlist_id INT AUTO_INCREMENT PRIMARY KEY,"
        "  user_id INT,"
        "  name VARCHAR(100),"
        "  FOREIGN KEY (user_id) REFERENCES users(user_id)"
        ")"
    )
    TABLES['playlist_songs'] = (
        "CREATE TABLE IF NOT EXISTS playlist_songs ("
        "  playlist_id INT,"
        "  song_id INT,"
        "  PRIMARY KEY (playlist_id, song_id),"
        "  FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id),"
        "  FOREIGN KEY (song_id) REFERENCES songs(song_id)"
        ")"
    )

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table {table_name}: ", end='')
            cursor.execute(table_description)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)

    cursor.close()
    conn.close()

except mysql.connector.Error as err:
    print(err)
