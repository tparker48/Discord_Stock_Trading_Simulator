import discord
from StockTraderLogic import StockTraderLogic

class MyClient(discord.Client):

    traderBot = None

    async def on_ready(self):
        self.traderBot = StockTraderLogic()
        print("logged on as {0}!".format(self.user))
        

    async def on_message(self, message):
        if self.tradeRelated(message):
            channel = message.channel
            print(message.author)
            response = self.traderBot.getResponse(message)
            print(response)
            await channel.send(response)


    def tradeRelated(self, message):
        text =  str(message.content)

        if len(text) >= 6:
            if text[:6].lower() == "trader":
                return True

        return False

try:
    f = open("token.txt", "r")
    token = f.readline()
    f.close()
    bot = MyClient()
    bot.run(token)
except:
    print("Couldn't get the token from \'token.txt\'!")