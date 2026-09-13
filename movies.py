from cassandra.cluster import Cluster
import uuid

# ==============================
# CQL Statements
# ==============================
CREATE_KEYSPACE = """
CREATE KEYSPACE IF NOT EXISTS movies
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
"""
CREATE_TABLE_MOVIE_BY_TITLE = """
CREATE TABLE IF NOT EXISTS movies_by_title (
        movie_id UUID, title TEXT,
        release_year INT, genre TEXT,
        rating FLOAT, director TEXT,
        PRIMARY KEY (title, release_year)
     ) WITH CLUSTERING ORDER BY (release_year DESC);
"""
CREATE_TABLE_MOVIE_BY_GENRE = """
CREATE TABLE IF NOT EXISTS movies_by_genre (
        movie_id UUID, title TEXT,
        release_year INT, genre TEXT,
        rating FLOAT, director TEXT,
        PRIMARY KEY (genre, rating, release_year)
     ) WITH CLUSTERING ORDER BY (rating DESC, release_year DESC);
"""
INSERT_MOVIE_TITLE = """
INSERT INTO movies_by_title
(title, release_year, director, genre, rating, movie_id)
VALUES (?,?,?,?,?,?);
"""
INSERT_MOVIE_GENRE = """
INSERT INTO movies_by_genre
(movie_id, title, release_year,
genre, rating, director)
VALUES (?, ?, ?, ?, ?, ?);
"""

DELETE_MOVIE_TITLE = """
DELETE FROM movies_by_title
WHERE title = ? AND release_year = ?;
"""
DELETE_MOVIE_GENRE = """
DELETE FROM movies_by_genre
WHERE genre = ? AND rating = ? AND movie_id = ?;
"""
SELECT_BY_TITLE = """
SELECT * FROM movies_by_title
WHERE title = ? AND release_year = ?;
"""

SELECT_BY_GENRE = """
SELECT * FROM movies_by_genre
WHERE genre = ?;
"""
UPDATE_MOVIE_DIRECTOR_TITLE = """
UPDATE movies_by_title
SET director = ?
WHERE title = ? AND release_year = ?;
"""
UPDATE_MOVIE_DIRECTOR_GENRE = """
UPDATE movies_by_genre
SET director = ?
WHERE genre = ? AND rating = ? AND release_year = ?;
"""
# ==============================
# Funciones base
# ==============================


def create_keyspace_and_tables(session):
    session.execute(CREATE_KEYSPACE)
    session.set_keyspace("movies")
    title_stmt = session.prepare(CREATE_TABLE_MOVIE_BY_TITLE)
    session.execute(title_stmt)
    genre_stmt = session.prepare(CREATE_TABLE_MOVIE_BY_GENRE)
    session.execute(genre_stmt)


def insert_movie(session, title, year, director, genre, rating):
    id = uuid.uuid4()
    title_stmt = session.prepare(INSERT_MOVIE_TITLE)
    session.execute(title_stmt, (title, year, director, genre, rating, id))
    genre_stmt = session.prepare(INSERT_MOVIE_GENRE)
    session.execute(genre_stmt, (id, title, year, genre, rating, director))


def query_by_title(session, title, year):
    stmt = session.prepare(SELECT_BY_TITLE)
    rows = session.execute(stmt, (title, year))
    for r in rows:
        print(f'\nTítulo: {r.title}\nAño de estreno: {r.release_year}\nDirector: {r.director}\nGénero: {r.genre}\nRating: {"{:2.1f}".format(r.rating)}')


def query_by_genre(session, genre):
    stmt = session.prepare(SELECT_BY_GENRE)
    rows = session.execute(stmt, (genre,))
    for r in rows:
        print(f'{r.title} ({r.director}) - {"{:2.1f}".format(r.rating)}\n', end='')


def update_movie_director(session, title, genre, release_year, rating, new_director):
    title_stmt = session.prepare(UPDATE_MOVIE_DIRECTOR_TITLE)
    genre_stmt = session.prepare(UPDATE_MOVIE_DIRECTOR_GENRE)
    session.execute(title_stmt, (new_director, title, release_year))
    session.execute(genre_stmt, (new_director, genre, rating, release_year))


def delete_movie(session, title, genre, rating, release_year):
    title_stmt = session.prepare(DELETE_MOVIE_TITLE)
    genre_stmt = session.prepare(DELETE_MOVIE_GENRE)
    session.execute(title_stmt, (title, release_year, rating))
    session.execute(genre_stmt, (release_year, genre, rating))
    print("Película eliminada")

# ==============================
# Menú
# ==============================


def main():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    create_keyspace_and_tables(session)

    while True:
        print("\n=== Movie Database Menu ===")
        print("1. Insertar película")
        print("2. Consultar por título")
        print("3. Consultar por género")
        print("4. Actualizar director")
        print("5. Eliminar película")
        print("0. Salir")
        choice = input("Seleccione opción: ")

        if choice == "1":
            title = input("Título: ")
            year = int(input("Año: "))
            director = input("Director: ")
            genre = input("Género: ")
            rating = float(input("Rating: "))
            insert_movie(session, title, year, director, genre, rating)
        elif choice == "2":
            title = input("Título: ")
            year = int(input("Año: "))
            query_by_title(session, title, year)
        elif choice == "3":
            genre = input("Género: ")
            query_by_genre(session, genre)
        elif choice == "4":
            title = input("Título: ")
            release_year = int(input("Año: "))
            genre = input("Género: ")
            rating = float(input("Rating: "))
            new_director = input("Nuevo Director: ")
            update_movie_director(session, title, genre, release_year, rating, new_director)
        elif choice == "5":
            # Eliminar de movie_by_title -> title, release_year
            # Eliminar de movie_by_genre -> genre, rating
            title = input("Título: ")
            release_year = input("Año: ")
            genre = input("Género: ")
            rating = input("Rating: ")
            delete_movie(session, title, genre, rating, release_year)
        elif choice == '0':
            # Cerrar conexión y salir
            cluster.shutdown()
            break
        else:
            print("Opción inválida")
            break


if __name__ == "__main__":
    main()
