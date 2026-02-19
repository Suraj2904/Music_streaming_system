import mysql.connector
import pygame
import hashlib



# Function to play audio
def play_audio(file_path):
    """
    Plays audio from the specified file path using pygame.

    Args:
        file_path (str): Path to the audio file (e.g., "my_audio.mp3").
    """
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        print("Playing audio... Press 'p' to pause, 'r' to resume, 'q' to quit.")

        running = True
        while running:
            command = input("Enter command (p: pause, r: resume, q: quit): ").strip().lower()
            if command == 'p':
                pygame.mixer.music.pause()
                print("Paused. Press 'r' to resume or 'q' to quit.")
            elif command == 'r':
                pygame.mixer.music.unpause()
                print("Resumed. Press 'p' to pause or 'q' to quit.")
            elif command == 'q':
                pygame.mixer.music.stop()
                running = False
            else:
                print("Invalid command. Please enter 'p', 'r', or 'q'.")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    finally:
        pygame.quit()



# Database connection setup
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sun",  # Ensure this is the correct password
        database="music_streaming_service"
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"Error: {str(err)}")
    exit(1)


# Utility functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        db.commit()
        return 'User registered successfully!'
    except mysql.connector.Error as err:
        return f'Error: {str(err)}'


def login_user(username, password):
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
    user = cursor.fetchone()
    if user:
        return 'Logged in successfully!'
    else:
        return 'Invalid credentials'


def get_songs():
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    return [{'song_id': song[0], 'title': song[1], 'artist': song[2], 'album': song[3], 'file_path': song[4]} for song
            in songs]


def add_song(title, artist, album, file_path):
    try:
        cursor.execute("INSERT INTO songs (title, artist, album, file_path) VALUES (%s, %s, %s, %s)",
                       (title, artist, album, file_path))
        db.commit()

        # Auto-clean any surrounding quotes from file_path for the newly inserted song
        song_id = cursor.lastrowid
        cursor.execute(
            "UPDATE songs SET file_path = REPLACE(REPLACE(file_path, %s, ''), %s, '') WHERE song_id = %s",
            ('"', "'", song_id)
        )
        db.commit()
        
        return 'Song added successfully!'
    except mysql.connector.Error as err:
        return f'Error: {str(err)}'


def delete_song(song_id):
    try:
        cursor.execute("SELECT * FROM songs WHERE song_id = %s", (song_id,))
        song = cursor.fetchone()
        if not song:
            return 'No song found with that ID.'
        
        cursor.execute("DELETE FROM playlist_songs WHERE song_id = %s", (song_id,))
        db.commit()
        cursor.execute("DELETE FROM songs WHERE song_id = %s", (song_id,))
        db.commit()

        return 'Song deleted successfully!'

    except mysql.connector.Error as err:
        return f'Error: {str(err)}'


def create_playlist(user_id, name):
    try:
        cursor.execute("INSERT INTO playlists (user_id, name) VALUES (%s, %s)", (user_id, name))
        db.commit()
        return 'Playlist created successfully!'
    except mysql.connector.Error as err:
        return f'Error: {str(err)}'


def add_song_to_playlist(playlist_id, song_id):
    try:
        cursor.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)", (playlist_id, song_id))
        db.commit()
        return 'Song added to playlist successfully!'
    except mysql.connector.Error as err:
        return f'Error: {str(err)}'


# Main Interface
def main():
    while True:
        print("\nMusic Streaming Service")
        print("1. Register")
        print("2. Login")
        print("3. Add Song")
        print("4. View Songs")
        print("5. Delete Song")
        print("6. Create Playlist")
        print("7. Add Song to Playlist")
        print("8. Play Song")
        print("9. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            print(register_user(username, password))

        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            print(login_user(username, password))

        elif choice == '3':
            title = input("Enter song title: ")
            artist = input("Enter artist: ")
            album = input("Enter album: ")
            file_path = input("Enter file path: ")
            print(add_song(title, artist, album, file_path))

        elif choice == '4':
            songs = get_songs()
            if songs:
                for song in songs:
                    print(
                        f"ID: {song['song_id']}, Title: {song['title']}, Artist: {song['artist']}, Album: {song['album']}, File Path: {song['file_path']}")
            else:
                print("No songs found.")

        elif choice == '5':
            song_id = input("Enter song ID to delete: ")
            print(delete_song(song_id))

        elif choice == '6':
            user_id = input("Enter user ID: ")
            name = input("Enter playlist name: ")
            print(create_playlist(user_id, name))

        elif choice == '7':
            playlist_id = input("Enter playlist ID: ")
            song_id = input("Enter song ID: ")
            print(add_song_to_playlist(playlist_id, song_id))

        elif choice == '8':
            songs = get_songs()
            if not songs:
                print("No songs available.")
                continue

            for s in songs:
                print(f"{s['song_id']}: {s['title']}")

            song_id = input("Enter song ID: ")
            cursor.execute("SELECT file_path FROM songs WHERE song_id = %s", (song_id,))
            path = cursor.fetchone()

            if path:
                play_audio(path[0])
            else:
                print("Song not found.")

        elif choice == '9':
            print("Thank you...")
            break

        else:
            print("Invalid choice, please try again.")

    # Close the database connection before exiting
    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
