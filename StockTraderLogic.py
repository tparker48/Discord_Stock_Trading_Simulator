import pickle
import stockquotes
from formatStrings import bold, block

BALANCE = "portfolio_balance"
STOCKS = "portfolio_stocks"

STARTING_BALANCE = 15000

class StockTraderLogic():
    
    portfolio = None


    def getUserName(self, message):
        return str(message.author)

    def getInformalName(self, message):
        return bold(str(message.author)[:-5])

    def getBalance(self):
        return self.portfolio[BALANCE]

    def getBalanceString(self):
        return bold(str(round(self.portfolio[BALANCE] , 2))) + " USD"

    
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
            return self.getInformalName(message) + " already has a portoflio.\nBalance = " + self.getBalanceString()
        
        else:
            newPortfolio = {BALANCE:STARTING_BALANCE, STOCKS: {}}
            self.portfolio = newPortfolio
            try:
                portfolioName = self.getPortfolioName(message)
                file = open(portfolioName,"wb")
                pickle.dump(newPortfolio, file)
                file.close()
            except:
                return "Error Creating Portfolio!"

            return "Portfolio created for " + self.getInformalName(message) + "!\nBalance = " + self.getBalanceString()

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

        response = self.getInformalName(message)+ "'s balance: " + self.getBalanceString() + "\n"
        response+= ticker + " is currently valued at " + str(price) + " USD\nYou can afford " + str(round(self.getBalance()/price,2)) + " shares maximum"

        return response


    def getInfo(self, message):
        response = "\n ---------- " + self.getInformalName(message) + "'s Portfolio" + " ---------- \n\n"

        balance = self.getBalance()
        stocks = [s for s in self.portfolio[STOCKS]]

        stockPrices = self.getStockPrices(stocks)

        if not stockPrices[0]:
            return stockPrices[1]
        else:
            stockPrices = stockPrices[1]
        
        investmentsTotal = 0
        response += "Investments:\n"

        for stock in stocks:
            amountStr = bold(str(round(self.portfolio[STOCKS][stock],2))) + " shares"
            tickerPadding = " " * (8 - len(stock))
            amountPadding = " " * (20 - len(amountStr))
            
            response += "     " + bold(stock) + " :" + tickerPadding + amountStr + amountPadding +  "(" + bold(str(round(stockPrices[stock]*self.portfolio[STOCKS][stock],2))) + " USD)\n"

            investmentsTotal += stockPrices[stock]*self.portfolio[STOCKS][stock]

        response += "\n"
        response += "Balance :            " + self.getBalanceString() +"\n"
        response += "Investments :    " + bold(str(round(investmentsTotal,2))) + "  USD\n\n"
        response += "Total Value :      " + bold(str(round(investmentsTotal + balance, 2))) + " USD\n"
        response += "Net Profit  :        " + bold(str(round(investmentsTotal + balance - STARTING_BALANCE, 2))) + " USD"

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
            response += "Your current balance is now " + self.getBalanceString() + "\n"
            return response

    def buyStock(self, ticker, amount, message):

        price = self.getStockPrice(ticker)
        if not price[0]:
            return price[1]
        else:
            price = price[1]

        if amount == "all":
            amount = self.getBalance() / price
        else:
             amount = float(amount)

        if amount <= 0.0:
            return "Please enter an amount larger than zero"

        cost = price * amount
        if cost > self.getBalance():
            return self.getInformalName(message)+ "'s balance: " + self.getBalanceString() + "\nYou can only afford " + str(round(self.getBalance()/price,2)) + " shares!"
        else:
            self.portfolio[BALANCE] -= cost
            if ticker in self.portfolio[STOCKS]:
                self.portfolio[STOCKS][ticker] += amount
            else:
                self.portfolio[STOCKS][ticker] = amount

            if not self.savePortfolio(message):
                return "Error saving the changes to your portfolio. Nothing was done."

            return "You now own " + str(self.portfolio[STOCKS][ticker]) + " shares of " + ticker + "!\n"
            

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
            response += "Your current balance is now " + self.getBalanceString() + "\n"
            return response

    def sellStock(self, ticker, amount ,message):
        if ticker not in self.portfolio[STOCKS]:
            return "You don't own any " + ticker + " shares!"

        price = self.getStockPrice(ticker)
        if not price[0]:
            return price[1]
        else:
            price = price[1]

        if amount == "all":
            amount = self.portfolio[STOCKS][ticker]
        else:
            amount = float(amount)

        if amount <= 0.0:
            return "Please enter an amount larger than zero"
        
        if self.portfolio[STOCKS][ticker] < amount:
            return "You only have " + str(self.portfolio[STOCKS][ticker]) + " shares of " + ticker + "!"

        else:
            value = price * amount
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
        response = ""

        if not self.hasPortfolio(message) and txt != "trader setup":
            response = "Hello " + self.getInformalName(message) + ", I see you do not have trading portfolio set up!\nPlease type \'trader setup\' to start one"
        
        elif lowtxt == "trader setup":
            response = self.createPortFolio(message)

        elif lowtxt == "trader info":
            response = self.getInfo(message)

        elif len(txt) >= 12 and lowtxt[:12] == "trader check":
            response = self.checkStocks(message)

        elif len(txt) >= 10 and lowtxt[:10] == "trader buy":
            response = self.buyStocks(message)

        elif len(txt) >= 11 and lowtxt[:11] == "trader sell":
            response = self.sellStocks(message)

        else:
            response = "What does \""+txt+"\" mean?"
        
        return response