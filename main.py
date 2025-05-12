from bot_forwarder_whitelist_v2 import app

import asyncio
from bot_forwarder_whitelist_v2 import app, keep_alive

async def main():
    print("🚀 Bot forwarder aktif via main.py ...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Jalankan keep_alive bersamaan dengan bot
    await keep_alive()

if __name__ == '__main__':
    asyncio.run(main())