from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, ContextTypes, filters, CommandHandler
import os

BOT_TOKEN = '7810200438:AAFvqVFURy4R3WJCDAqL2taVPCywvUh3lJ8'

GROUPS = {
    'kolpri': -1002642043034,
    'trakteer': -1002277543739,
    'global': -1002322327832  # Mohon ganti dengan ID grup global yang benar
}

WHITELIST = {7629527598, 1135046298, 7559461392}


async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("✅ Cache telah direset!")


async def start_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in WHITELIST:
        await update.message.reply_text(
            "🚫 Kamu tidak diizinkan menggunakan bot ini.")
        return

    if update.message and update.message.forward_date:
        msg = update.message
        # Hanya simpan pesan dengan foto atau video
        if msg.photo or msg.video:
            # Simpan hanya media tanpa caption
            if msg.photo:
                context.user_data.setdefault('forwarded_msgs', []).append({
                    'type':
                    'photo',
                    'file_id':
                    msg.photo[-1].file_id,
                    'chat_id':
                    msg.chat_id,
                    'message_id':
                    msg.message_id
                })
            elif msg.video:
                context.user_data.setdefault('forwarded_msgs', []).append({
                    'type':
                    'video',
                    'file_id':
                    msg.video.file_id,
                    'chat_id':
                    msg.chat_id,
                    'message_id':
                    msg.message_id
                })

            count = len(context.user_data['forwarded_msgs'])

        # Track media types
        msg = update.message
        if msg.photo:
            context.user_data.setdefault('photo_count', 0)
            context.user_data['photo_count'] += 1
        elif msg.video:
            context.user_data.setdefault('video_count', 0)
            context.user_data['video_count'] += 1
        elif msg.text:
            context.user_data.setdefault('text_count', 0)
            context.user_data['text_count'] += 1

        # Show status every 50 media
        if count % 50 == 0:
            status = f"""
📊 Status Pengiriman:
• Total media: {count} file
• Foto: {context.user_data.get('photo_count', 0)} file
• Video: {context.user_data.get('video_count', 0)} file
• Teks: {context.user_data.get('text_count', 0)} file
• Status: {count} media telah diterima.
            """
            await update.message.reply_text(status)

        if not context.user_data.get('waiting_for_more'):
            context.user_data['waiting_for_more'] = True
            await update.message.reply_text(
                "📤 Silakan kirim semua media yang ingin diteruskan.\n\nKetik /selesai untuk melanjutkan ke langkah berikutnya."
            )
        return


async def done_forwarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('forwarded_msgs'):
        await update.message.reply_text("⚠️ Belum ada media yang dikirim!")
        return

    await update.message.reply_text(
        "✍️ Masukkan deskripsi untuk semua media ini:")
    context.user_data['waiting_for_description'] = True

    count = len(context.user_data.get('forwarded_msgs', []))
    target = 300  # Target jumlah media
    remaining = target - count if count < target else 0

    status = f"""
📊 Status Pengiriman:
• Total media saat ini: {count} file
• Media yang belum: {remaining} file
• Foto: {context.user_data.get('photo_count', 0)} file
• Video: {context.user_data.get('video_count', 0)} file
• Teks: {context.user_data.get('text_count', 0)} file
    """

    buttons = [[
        InlineKeyboardButton("✍️ Lanjut Buat Deskripsi",
                             callback_data="action_continue"),
        InlineKeyboardButton("➕ Tambah Media", callback_data="action_add")
    ],
               [
                   InlineKeyboardButton("⏳ Tunggu",
                                        callback_data="action_wait"),
                   InlineKeyboardButton("🔄 Reset",
                                        callback_data="action_reset")
               ]]

    await update.message.reply_text(status,
                                    reply_markup=InlineKeyboardMarkup(buttons))
    context.user_data['confirming_action'] = True
    return

    count = len(context.user_data['forwarded_msgs'])
    confirmation = f"""
📊 Status Pengiriman Final:
• Total media: {count} file
• Foto: {context.user_data.get('photo_count', 0)} file
• Video: {context.user_data.get('video_count', 0)} file
• Teks: {context.user_data.get('text_count', 0)} file
• Status: Menunggu konfirmasi ⏳

Apakah semua media yang dikirim sudah lengkap?
Ketik 'ya' jika sudah lengkap
Ketik 'tidak' jika belum lengkap dan ingin menambah media lagi
    """
    context.user_data['confirming_done'] = True
    await update.message.reply_text(confirmation)


async def receive_description(update: Update,
                              context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in WHITELIST:
        await update.message.reply_text(
            "🚫 Kamu tidak diizinkan menggunakan bot ini.")
        return

    if not context.user_data.get('forwarded_msgs'):
        await update.message.reply_text(
            "⚠️ Kirim pesan yang sudah di-forward dulu.")
        return

    description = update.message.text.strip()
    context.user_data['description'] = description

    buttons = [[InlineKeyboardButton("🔥 KOLPRI", callback_data="kolpri")],
               [InlineKeyboardButton("🏱 TRAKTEER", callback_data="trakteer")],
               [InlineKeyboardButton("🌐 GLOBAL", callback_data="global")]]
    await update.message.reply_text("🔄 Kirim ke grup mana?",
                                    reply_markup=InlineKeyboardMarkup(buttons))


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("action_"):
        action = query.data.replace("action_", "")

        if action == "continue":
            buttons = [
                [InlineKeyboardButton("🔥 KOLPRI", callback_data="kolpri")],
                [InlineKeyboardButton("🏱 TRAKTEER", callback_data="trakteer")],
                [InlineKeyboardButton("🌐 GLOBAL", callback_data="global")]
            ]
            await query.edit_message_text(
                "🔄 Kirim ke grup mana?",
                reply_markup=InlineKeyboardMarkup(buttons))
            context.user_data['waiting_for_description'] = True
            context.user_data['confirming_action'] = False
        elif action == "add":
            context.user_data['waiting_for_more'] = True
            context.user_data['confirming_action'] = False
            await query.edit_message_text("📤 Silakan kirim media tambahan.")
        elif action == "wait":
            await query.edit_message_text(
                "⏳ Baik, silakan gunakan /selesai nanti untuk melanjutkan.")
            context.user_data['confirming_action'] = False
        elif action == "reset":
            context.user_data.clear()
            await query.edit_message_text(
                "🔄 Bot telah direset. Silakan mulai dari awal.")
        return

    # Handle group selection
    if query.data in GROUPS:
        user_id = query.from_user.id
        if user_id not in WHITELIST:
            await query.answer("🚫 Tidak diizinkan.", show_alert=True)
            return

        target = query.data
        forwarded_msgs = context.user_data.get('forwarded_msgs', [])
        description = context.user_data.get('description', '')

    if not forwarded_msgs:
        await query.edit_message_text("⚠️ Tidak ada pesan yang bisa dikirim.")
        return

    if target not in GROUPS:
        await query.edit_message_text("⚠️ Nama grup tidak dikenali.")
        return

    try:
        # Kirim deskripsi jika ada
        if description:
            await context.bot.send_message(chat_id=GROUPS[target],
                                           text=description)

        # Kirim media sebagai grup
        import asyncio
        from telegram.error import RetryAfter
        from telegram import InputMediaPhoto, InputMediaVideo

        async def send_media_group(media_group, retries=3):
            for attempt in range(retries):
                try:
                    await context.bot.send_media_group(chat_id=GROUPS[target],
                                                       media=media_group)
                    return True
                except RetryAfter as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(e.retry_after)
                        continue
                    raise
                except Exception as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
                        continue
                    raise
            return False

        # Bagi media menjadi grup-grup 10
        media_chunks = []
        current_chunk = []

        for msg in forwarded_msgs:
            media_item = None
            if msg['type'] == 'photo':
                media_item = InputMediaPhoto(media=msg['file_id'])
            elif msg['type'] == 'video':
                media_item = InputMediaVideo(media=msg['file_id'])

            if media_item:
                current_chunk.append(media_item)
                if len(current_chunk) == 10:
                    media_chunks.append(current_chunk)
                    current_chunk = []

        # Tambahkan sisa media jika ada
        if current_chunk:
            media_chunks.append(current_chunk)

        # Kirim setiap grup secara berurutan
        total_chunks = len(media_chunks)
        for i, chunk in enumerate(media_chunks, 1):
            success = await send_media_group(chunk)
            if not success:
                await query.edit_message_text(
                    f"❌ Gagal mengirim grup media {i}/{total_chunks}")
                return
            await asyncio.sleep(1)  # Delay lebih lama antar grup

        await query.edit_message_text(f"✅ Dikirim ke grup *{target.upper()}*",
                                      parse_mode="Markdown")
    except Exception as e:
        error_msg = str(e)
        if "Message text is empty" in error_msg:
            # Lanjutkan pengiriman media tanpa deskripsi
            for msg in forwarded_msgs:
                if msg['type'] == 'photo':
                    await context.bot.send_photo(chat_id=GROUPS[target],
                                                 photo=msg['file_id'])
                elif msg['type'] == 'video':
                    await context.bot.send_video(chat_id=GROUPS[target],
                                                 video=msg['file_id'])
            await query.edit_message_text(
                f"✅ Media terkirim ke grup *{target.upper()}* tanpa deskripsi",
                parse_mode="Markdown")
        else:
            await query.edit_message_text(f"❌ Gagal mengirim: {error_msg}")

    context.user_data.clear()


# Builder untuk di-panggil dari main.py
import telegram
import asyncio


async def keep_alive():
    while True:
        try:
            await asyncio.sleep(60)
            print("Bot still running...")
            await app.bot.get_me()  # Test connection
        except Exception as e:
            print(f"Keep alive error: {e}")
            try:
                await app.initialize()
                await app.start()
            except Exception as re:
                print(f"Restart error: {re}")
            await asyncio.sleep(5)
            continue


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error occurred: {context.error}")
    from telegram.error import Conflict
    if isinstance(context.error, Conflict):
        print("Bot conflict detected - another instance might be running")
        # Restart polling after conflict
        await asyncio.sleep(5)
        await app.initialize()
        await app.start()
        await app.updater.start_polling()


app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_error_handler(error_handler)
app.add_handler(CommandHandler("reset", reset_handler))
app.add_handler(CommandHandler("selesai", done_forwarding))
app.add_handler(
    MessageHandler(
        filters.FORWARDED & (filters.TEXT | filters.PHOTO | filters.VIDEO),
        start_forward))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.FORWARDED,
                   receive_description))
app.add_handler(CallbackQueryHandler(handle_callback))
