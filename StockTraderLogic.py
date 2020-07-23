import pickle
import stockquotes

BALANCE = "portfolio_balance"
STOCKS = "portfolio_stocks"

class StockTraderLogic():
    
    portfolio = None


    def getUserName(self, message):
        return str(message.author)

    def getInformalName(self, message):
        return str(message.author)[:-5]


    def getPortfolioName(self, message):
        return "portfolios/" + self.getUserName(message)+"_portfolio"

    def hasPortfolio(self, message):
        portfolioName = self.getPortfolioName(message)
        try:
            file = open(portfolioName,"rb")
            self.portfolio = pickle.load(file)
            file.close()
            return True
        except:
            return False

    def createPortFolio(self, message):
        if self.hasPortfolio(message):
            return self.getInformalName(message) + " already has a portoflio.\nCurrent Balance = " + str(self.portfolio[BALANCE])
        
        else:
            newPortfolio = {BALANCE:15000, STOCKS: {}}

            try:
                portfolioName = self.getPortfolioName(message)
                file = open(portfolioName,"wb")
                self.portfolio = pickle.dump(newPortfolio, file)
                file.close()
            except:
                return "Error Creating Portfolio!"

            return "Portfolio created for " + self.getInformalName(message) + "!\nCurrent Balance = " + str(newPortfolio[BALANCE]) 

    def savePortfolio(self, message):
        try:
            file = open(self.getPortfolioName(message),'wb')
            pickle.dump(self.portfolio, file)
            file.close()
        except:
            return False

        return True


    def getStockPrice(self, ticker):
        results = self.getStockPrices([ticker])
        if results[0]:
            return [results[0], results[1][ticker]]
        else:
            return results

    def getStockPrices(self, tickers):
        prices = {}

        for ticker in tickers:
            try:
                info = stockquotes.Stock(ticker)
                prices[ticker] = info.current_price
            except:
                return [False, "Uh oh! Couldn't find " + ticker + ", did you type that correctly?"]

        return [True, prices]

    def checkStocks(self, message):
        ticker = str(message.content)[12:].strip()
        price = self.getStockPrice(ticker)
        if not price[0]:
            return price[1]
        else:
            price = price[1]

        response = self.getInformalName(message)+ "'s balance: " + str(self.portfolio[BALANCE]) + "\n"
        response+= ticker + " is currently valued at " + str(price) + " USD\nYou can afford " + str(round(self.portfolio[BALANCE]/price,2)) + " shares maximum"

        return response


    def getInfo(self, message):
        response = self.getInformalName(message) + "'s Portfolio:\n"

        balance = self.portfolio[BALANCE]
        stocks = [s for s in self.portfolio[STOCKS]]

        stockPrices = self.getStockPrices(stocks)

        if not stockPrices[0]:
            return stockPrices[1]
        else:
            stockPrices = stockPrices[1]
        
        total = balance
        response += "Current Balance: " + str(round(balance,2)) +"\n\n"
        response += "Investments:\n"

        for stock in stocks:
            total += stockPrices[stock]*self.portfolio[STOCKS][stock]
            response += "     " + stock + ": " + str(self.portfolio[STOCKS][stock]) + " shares  -------- " + str(stockPrices[stock]) + " USD per share (worth " + str(round(stockPrices[stock]*self.portfolio[STOCKS][stock],2)) + " USD)\n"

        response += "\nValue: " + str(total) + " USD"

        return response
        


    def buyStocks(self, message):
        response = ""
        request = str(message.content)[10:].strip().split()
        if len(request)%2 != 0:
            return "Uh oh!\nPlease type \"trader buy STOCK> AMOUNT\"\nFor multiple purchases, try \"trader buy STOCK1 AMOUNT1 STOCK2 AMOUNT2 ...\""
        else:
            for i in range(int(len(request)/2)):
                index = i*2
                ticker = request[index]
                amount = request[index+1]
                print("Processing Buy Request for " + amount + " shares of " + ticker)
                buyResponse = self.buyStock(ticker, amount, message)
                
                response += buyResponse
                if "You now own" not in buyResponse:
                    return response
            response += "Your current balance is now " + str(round(self.portfolio[BALANCE],2)) + "\n"
            return response

    def buyStock(self, ticker, amount, message):

        price = self.getStockPrice(ticker)
        if not price[0]:
            return price[1]
        else:
            price = price[1]

        if amount == "all":
            amount = self.portfolio[BALANCE] / price
        else:
             amount = float(amount)

        if amount <= 0.0:
            return "Please enter an amount larger than zero"

        cost = price * amount
        if cost > self.portfolio[BALANCE]:
            return self.getInformalName(message)+ "'s balance: " + str(self.portfolio[BALANCE]) + "\nYou can only afford " + str(round(self.portfolio[BALANCE]/price,2)) + " shares!"
        else:
            self.portfolio[BALANCE] -= cost
            if ticker in self.portfolio[STOCKS]:
                self.portfolio[STOCKS][ticker] += amount
            else:
                self.portfolio[STOCKS][ticker] = amount

            if not self.savePortfolio(message):
                return "Error saving the changes to your portfolio. Nothing was done."

            return "You now own " + str(self.portfolio[STOCKS][ticker]) + " shares of " + ticker + "!\n"
            
#return "Uh oh!\nPlease type \"trader sell STOCK AMOUNT\""
    def sellStocks(self, message):
        response = ""
        
        request = str(message.content)[11:].strip().split()
        if len(request)%2 != 0:
            return "Uh oh!\nPlease type \"trader sell STOCK> AMOUNT\"\nFor multiple, try \"trader sell STOCK1 AMOUNT1 STOCK2 AMOUNT2 ...\""
        else:
            for i in range(int(len(request)/2)):
                index = i*2
                ticker = request[index]
                amount = request[index+1]
                print("Processing Sell Request for " + amount + " shares of " + ticker)
                sellResponse = self.sellStock(ticker, amount, message)
                
                response += sellResponse
                if "You now own" not in sellResponse and "You sold" not in sellResponse:
                    return response
            response += "Your current balance is now " + str(round(self.portfolio[BALANCE],2)) + "\n"
            return response

    def sellStock(self, ticker, amount ,message):
        price = self.getStockPrice(ticker)
        if not price[0]:
            return price[1]
        else:
            price = price[1]

        if amount == "all":
            if ticker not in self.portfolio[STOCKS]:
                return "You don't own any " + ticker + " shares!"
            else:
                amount = self.portfolio[STOCKS][ticker]
        else:
            amount = float(amount)

        if amount <= 0.0:
            return "Please enter an amount larger than zero"

        value = price * amount
        
        if ticker not in self.portfolio[STOCKS]:
            return "You don't own any " + ticker + " shares!"

        elif self.portfolio[STOCKS][ticker] < amount:
            return "You only have " + str(self.portfolio[STOCKS][ticker]) + " shares of " + ticker + "!"

        else:
            self.portfolio[BALANCE] += value
            self.portfolio[STOCKS][ticker] -= amount

            if self.portfolio[STOCKS][ticker] == 0.0:
                del(self.portfolio[STOCKS][ticker])

            if not self.savePortfolio(message):
                return "Error saving the changes to your portfolio. No shares of " + ticker + " were purchased."

            if ticker in self.portfolio[STOCKS]:
                return "You now own " + str(self.portfolio[STOCKS][ticker]) + " shares of " + ticker + "!\n"
            else:
                return "You sold all your " + ticker + " shares!\n"


    def getResponse(self, message):
        txt = str(message.content)
        lowtxt = txt.lower()

        if not self.hasPortfolio(message) and txt != "trader setup":
            return "Hello " + self.getInformalName(message) + ", I see you do not have trading portfolio set up!\nPlease type \'trader setup\' to start one"
        
        elif lowtxt == "trader setup":
            return self.createPortFolio(message)

        elif lowtxt == "trader info":
            return self.getInfo(message)

        elif len(txt) >= 12 and lowtxt[:12] == "trader check":
            return self.checkStocks(message)

        elif len(txt) >= 10 and lowtxt[:10] == "trader buy":
            return self.buyStocks(message)

        elif len(txt) >= 11 and lowtxt[:11] == "trader sell":
            return self.sellStocks(message)

        return "What does \""+txt+"\" mean?"