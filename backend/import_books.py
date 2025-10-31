"""
Script to import books from CSV into database with vector embeddings.
"""
import pandas as pd
import sqlite3
import os
from sentence_transformers import SentenceTransformer

# Paths
CSV_PATH = "/Users/kaze/Projects/gandhi_exel/libros_populares_corregido.csv"
DB_PATH = "db/conversation.db"
DB_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR0_PATH = os.path.join(DB_DIR, "db", "vector0.dylib")
VSS0_PATH = os.path.join(DB_DIR, "db", "vss0.dylib")

# Load sentence transformer model
print("Cargando modelo de embeddings...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Modelo cargado.")

# Genre to section mapping
GENRE_TO_SECTION = {
    "infantiles": "Infantil",
    "infantiles de 3 a 6 años": "Infantil",
    "juveniles": "Infantil",
    "autoayuda": "General",
    "crecimiento personal": "General",
    "filosofía": "General",
    "familia": "General",
    "literatura": "Ficción",
    "literatura histórica": "Ficción",
    "literatura policíaca": "Ficción",
    "biografía novelada": "Ficción",
    "libros para todos": "Bestsellers",
    "novela": "Ficción"
}


def assign_section(genre):
    """Assign section based on genre."""
    genre_lower = genre.lower()
    for key, section in GENRE_TO_SECTION.items():
        if key in genre_lower:
            return section
    return "Novedad"  # Default


def create_virtual_table(conn):
    """Create virtual table for vector search."""
    cursor = conn.cursor()

    # Create virtual table for embeddings
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS vss_books USING vss0(
            embedding(384)
        )
    """)

    conn.commit()


def clear_existing_books(cursor):
    """Clear all existing books and embeddings."""
    print("🗑️  Limpiando libros existentes...")

    # Delete all embeddings
    cursor.execute("DELETE FROM vss_books")

    # Delete all books
    cursor.execute("DELETE FROM books")

    print("✅ Base de datos limpiada.")


def import_books():
    """Import books from CSV to database."""
    print("Leyendo CSV...")
    df = pd.read_csv(CSV_PATH)

    # Filter only books in stock
    df = df[df['existencia'] == True]
    print(f"Total de libros en existencia: {len(df)}")

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)

    # Load extensions
    print("Cargando extensiones sqlite-vec...")
    conn.load_extension(VECTOR0_PATH.replace('.dylib', ''))
    conn.load_extension(VSS0_PATH.replace('.dylib', ''))
    conn.enable_load_extension(False)

    cursor = conn.cursor()

    # Create books table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            genero TEXT NOT NULL,
            sinopsis TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            disponibilidad BOOLEAN DEFAULT TRUE,
            estante TEXT NOT NULL
        )
    """)

    # Create virtual table for vector search
    create_virtual_table(conn)

    # Clear existing data before importing
    clear_existing_books(cursor)
    conn.commit()

    print("Importando libros...")
    imported = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            titulo = row['nombre del libero']
            autor = row['autor(es)']
            genero = row['genero(s)']
            sinopsis = row['sinopsis'] if pd.notna(row['sinopsis']) else ""
            isbn = row['isbn']
            estante = assign_section(genero)

            # Generate embedding for title + synopsis
            text_to_embed = f"{titulo} {sinopsis}"
            embedding = model.encode(text_to_embed)

            # Insert book
            cursor.execute("""
                INSERT OR IGNORE INTO books (titulo, autor, genero, sinopsis, isbn, disponibilidad, estante)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (titulo, autor, genero, sinopsis, str(isbn), True, estante))

            if cursor.lastrowid > 0:
                book_id = cursor.lastrowid

                # Insert embedding into virtual table
                cursor.execute("""
                    INSERT INTO vss_books(rowid, embedding)
                    VALUES (?, ?)
                """, (book_id, embedding.tobytes()))

                imported += 1
                if imported % 50 == 0:
                    print(f"Importados: {imported}")
            else:
                skipped += 1

        except Exception as e:
            print(f"Error importando libro {isbn}: {e}")
            skipped += 1
            continue

    conn.commit()
    conn.close()

    print(f"\n✅ Importación completada!")
    print(f"   Importados: {imported}")
    print(f"   Omitidos: {skipped}")


if __name__ == "__main__":
    import_books()
