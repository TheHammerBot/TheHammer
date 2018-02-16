from thehammer import make_bot

bot = make_bot()

try:
    bot.run_bot()
except KeyboardInterrupt:
    bot.shutdown()