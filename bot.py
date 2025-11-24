import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler

TOKEN = 8598781833:AAE-k3bezoFbYUoxw6nUbIQj8ye2KbN84Tkos.environ.get("TOKEN")
ADMIN_USER_ID = 6352160630int(os.environ.get("ADMIN_USER_ID", "123456789"))

logging.basicConfig(level=logging.INFO)
BOT_NAME, REFERRAL_LINK, DESCRIPTION = range(3)
campaigns_db, users_db = {}, set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_db.add(update.effective_user.id)
    await update.message.reply_text("👋 ¡Bienvenido! Recibirás promociones de bots. 🎁")

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID: return
    await update.message.reply_text("🛠️ Panel Admin:\n/crear - Crear campaña\n/enviar - Enviar campaña\n/estadisticas - Stats")

async def crear_campaña(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID: return
    await update.message.reply_text("🚀 **Nombre del bot:**")
    return BOT_NAME

async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nombre_bot'] = update.message.text
    await update.message.reply_text("📝 **Enlace de referido:**")
    return REFERRAL_LINK

async def recibir_enlace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['enlace'] = update.message.text
    await update.message.reply_text("📋 **Descripción:**")
    return DESCRIPTION

async def recibir_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['descripcion'] = update.message.text
    campaign_id = len(campaigns_db) + 1
    campaigns_db[campaign_id] = {
        'nombre': context.user_data['nombre_bot'],
        'enlace': context.user_data['enlace'],
        'descripcion': context.user_data['descripcion']
    }
    await update.message.reply_text(f"🎉 **¡Campaña Creada!** ID: #{campaign_id}\nUsa /enviar")
    context.user_data.clear()
    return ConversationHandler.END

async def ver_campañas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID: return
    if not campaigns_db: await update.message.reply_text("📭 No hay campañas"); return
    mensaje = "📋 **Campañas:**\n"
    for id_camp, camp in campaigns_db.items(): mensaje += f"🆔 #{id_camp} - {camp['nombre']}\n"
    await update.message.reply_text(mensaje)

async def enviar_campaña(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID: return
    if not campaigns_db: await update.message.reply_text("❌ No hay campañas"); return
    keyboard = [[InlineKeyboardButton(f"#{id} - {camp['nombre']}", callback_data=f"enviar_{id}")] for id, camp in campaigns_db.items()]
    await update.message.reply_text("📤 **Selecciona campaña:**", reply_markup=InlineKeyboardMarkup(keyboard))

async def ejecutar_envio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    id_campaña = int(query.data.split('_')[1])
    campaña = campaigns_db.get(id_campaña)
    if not campaña: await query.edit_message_text("❌ No encontrada"); return
    await query.edit_message_text("🔄 Enviando...")
    mensaje = f"🎉 **¡Promoción!**\n🤖 **{campaña['nombre']}**\n{campaña['descripcion']}\n🔗 {campaña['enlace']}"
    enviados = fallidos = 0
    for user_id in users_db:
        try: await context.bot.send_message(chat_id=user_id, text=mensaje); enviados += 1
        except: fallidos += 1
    await query.edit_message_text(f"✅ **Completado**\n✅ {enviados} | ❌ {fallidos}")

async def estadisticas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID: return
    await update.message.reply_text(f"📊 **Stats**\n👥 {len(users_db)} usuarios\n📢 {len(campaigns_db)} campañas")

def main():
    app = Application.builder().token(TOKEN).build()
    crear_handler = ConversationHandler(entry_points=[CommandHandler('crear', crear_campaña)], states={
        BOT_NAME: [MessageHandler(filters.TEXT, recibir_nombre)],
        REFERRAL_LINK: [MessageHandler(filters.TEXT, recibir_enlace)],
        DESCRIPTION: [MessageHandler(filters.TEXT, recibir_descripcion)]}, fallbacks=[])
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_start))
    app.add_handler(CommandHandler("estadisticas", estadisticas))
    app.add_handler(CommandHandler("campañas", ver_campañas))
    app.add_handler(CommandHandler("enviar", enviar_campaña))
    app.add_handler(crear_handler)
    app.add_handler(CallbackQueryHandler(ejecutar_envio, pattern='^enviar_'))
    print("🤖 Bot activo!")
    app.run_polling()

if __name__ == '__main__': main()
