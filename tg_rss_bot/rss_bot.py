import sqlite3
import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

# 初始化数据库连接
conn = sqlite3.connect('rss_subscriptions.db', check_same_thread=False)
c = conn.cursor()

# 创建数据库表
c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
              user_id INTEGER,
              rss_url TEXT
            )''')
c.execute('''CREATE TABLE IF NOT EXISTS feed_updates (
              rss_url TEXT PRIMARY KEY,
              last_updated TEXT
            )''')
conn.commit()

rss_feeds = {}

def load_subscriptions():
    c.execute("SELECT user_id, rss_url FROM subscriptions")
    rows = c.fetchall()
    
    for row in rows:
        user_id, rss_url = row
        if user_id not in rss_feeds:
            rss_feeds[user_id] = []
        rss_feeds[user_id].append(rss_url)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("欢迎使用RSS订阅Bot！使用 /subscribe <RSS URL> 来订阅一个RSS源。")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    rss_url = ' '.join(context.args)
    
    if rss_url:
        c.execute("INSERT INTO subscriptions (user_id, rss_url) VALUES (?, ?)", (user_id, rss_url))
        conn.commit()
        if user_id not in rss_feeds:
            rss_feeds[user_id] = []
        rss_feeds[user_id].append(rss_url)
        await update.message.reply_text(f"已成功订阅: {rss_url}")
    else:
        await update.message.reply_text("请提供有效的RSS URL。")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    rss_url = ' '.join(context.args)
    
    c.execute("DELETE FROM subscriptions WHERE user_id = ? AND rss_url = ?", (user_id, rss_url))
    conn.commit()
    
    if user_id in rss_feeds and rss_url in rss_feeds[user_id]:
        rss_feeds[user_id].remove(rss_url)
        await update.message.reply_text(f"已取消订阅: {rss_url}")
    else:
        await update.message.reply_text("你没有订阅这个RSS源。")

async def check_rss_updates(context: ContextTypes.DEFAULT_TYPE):
    for user_id, feeds in rss_feeds.items():
        for rss_url in feeds:
            feed = feedparser.parse(rss_url)
            if feed.entries:
                latest_entry = feed.entries[0]
                c.execute("SELECT last_updated FROM feed_updates WHERE rss_url = ?", (rss_url,))
                row = c.fetchone()
                
                if row is None or latest_entry.published > row[0]:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"最新更新: {latest_entry.title}\n{latest_entry.link}"
                    )
                    c.execute("REPLACE INTO feed_updates (rss_url, last_updated) VALUES (?, ?)", 
                              (rss_url, latest_entry.published))
                    conn.commit()

def main():
    load_subscriptions()

    application = Application.builder().token("7378539410:AAG7GF9QAcsfiMQwbCXjxmf5-7hOxj_Kwec").build()

    # 注册命令处理程序
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # 设置定时任务来检查RSS更新
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_rss_updates, 'interval', minutes=10, args=[application])
    scheduler.start()

    # 开始Bot
    application.run_polling()

if __name__ == '__main__':
    main()
