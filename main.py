import pyodbc
from PIL import Image
import io
import pillow_heif

# Configurações de conexão
connection_string = "teste"

def fetch_heic_image(cursor, image_id):
    cursor.execute("SELECT Conteudo, TipoMIME FROM TransporteMercadoriaFoto WHERE IDTransporteMercadoriaFoto = ?", image_id)
    row = cursor.fetchone()
    if row:
        return row.Conteudo, row.TipoMIME
    else:
        raise Exception("Image not found.")

def convert_heic_to_jpg(heic_data):
    heif_file = pillow_heif.read_heif(heic_data)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        return output.getvalue()

def update_image(cursor, image_id, jpg_data):
    cursor.execute(
        "UPDATE TransporteMercadoriaFoto SET Conteudo = ?, TipoMIME = ? WHERE IDTransporteMercadoriaFoto = ?",
        jpg_data,
        "image/jpeg",
        image_id,
    )
    cursor.commit()

def main(image_id):
    # Conecte ao banco de dados
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    try:
        # Passo 1: Buscar a imagem HEIC do banco de dados
        heic_data, mime_type = fetch_heic_image(cursor, image_id)
        
        if mime_type != "image/heic":
            raise Exception("The image is not in HEIC format.")

        # Passo 2: Converter a imagem HEIC para JPG
        jpg_data = convert_heic_to_jpg(heic_data)

        # Passo 3: Atualizar o banco de dados com a imagem convertida em JPG
        update_image(cursor, image_id, jpg_data)
        print("Image converted and updated successfully.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    i = 1
    while(i < 85):
        main(i)
        i+=1
