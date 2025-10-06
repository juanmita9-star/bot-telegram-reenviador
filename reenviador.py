import asyncio
import os # <-- AÑADE ESTA LÍNEA
from telegram import Bot

# --- CONFIGURACIÓN: AHORA SE LEE DE VARIABLES DE ENTORNO ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CANAL_ORIGEN_ID = int(os.environ.get("CANAL_ORIGEN_ID"))
CANAL_DESTINO_ID = int(os.environ.get("CANAL_DESTINO_ID"))
PALABRA_CLAVE = os.environ.get("PALABRA_CLAVE", "LIVE") # Usará LIVE si no se especifica
# -----------------------------------------------------------

# Variable para guardar el ID del último mensaje procesado
ultimo_mensaje_id = 0

async def main():
    global ultimo_mensaje_id
    bot = Bot(token=BOT_TOKEN)
    
    print("Bot iniciado. Escuchando nuevos mensajes...")

    # Obtenemos las últimas actualizaciones para saber desde dónde empezar
    try:
        updates = await bot.get_updates(offset=-1, limit=1, timeout=0)
        if updates:
            ultimo_mensaje_id = updates[0].update_id + 1
            print(f"Empezando a procesar desde la actualización: {ultimo_mensaje_id}")
    except Exception as e:
        print(f"Error al obtener la primera actualización: {e}")

    # Bucle infinito para escuchar perpetuamente
    while True:
        try:
            # Pedimos a Telegram las nuevas actualizaciones (mensajes)
            updates = await bot.get_updates(offset=ultimo_mensaje_id, timeout=20)

            for update in updates:
                # Nos aseguramos de procesar solo mensajes de canal
                if update.channel_post:
                    mensaje = update.channel_post
                    # Comprobamos si el mensaje es del canal de origen que nos interesa
                    if mensaje.chat.id == CANAL_ORIGEN_ID:
                        # Comprobamos si el texto del mensaje contiene la palabra clave
                        # (ignorando mayúsculas/minúsculas)
                        if mensaje.text and PALABRA_CLAVE.lower() in mensaje.text.lower():
                            print(f"¡Palabra clave '{PALABRA_CLAVE}' encontrada! Reenviando mensaje...")
                            # Reenviamos el mensaje al canal de destino
                            await bot.forward_message(
                                chat_id=CANAL_DESTINO_ID,
                                from_chat_id=CANAL_ORIGEN_ID,
                                message_id=mensaje.message_id
                            )
                            print("Mensaje reenviado con éxito.")
                
                # Actualizamos el ID para no volver a procesar este mensaje
                ultimo_mensaje_id = update.update_id + 1

        except Exception as e:
            print(f"Ocurrió un error: {e}. Reintentando en 10 segundos...")
            await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:

        print("\nBot detenido manualmente.")
