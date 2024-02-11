import telegram,asyncio
import time,sys
import requests
from telegram.constants import ParseMode

class liquidty_wizard:
    def getPoolLength(self,factoryContract):
        poolLength = factoryContract.functions.allPairsLength().call()
        return poolLength

    #fetching pool addresses from camelot factory
    def scanFactory(self,factoryContract,initialPoolLength):
        initialTotalIndex = int(initialPoolLength) - 1

        updatedPoolLength = factoryContract.functions.allPairsLength().call()
        print(updatedPoolLength)
        #time.sleep(12345)
        updatedTotalIndex = int(updatedPoolLength) - 1

        totalAddedIndex = int(updatedTotalIndex) - initialTotalIndex 
        if totalAddedIndex >= 1:
            PoolAdresses = [factoryContract.functions.allPairs(initialTotalIndex + index).call() for index in range(1,totalAddedIndex +1)]
            return PoolAdresses,updatedPoolLength
        else:
            return 'None',updatedPoolLength
        
    #Geting the actual token pair
    def pooledTokens(self,connect,poolContract,WETHUSDTUSDC):
        token0 = connect.to_checksum_address(poolContract.functions.token0().call())
        token1 = connect.to_checksum_address(poolContract.functions.token1().call())
        print(f'token0:{token0}\ntoken1:{token1}')
        if token0 in WETHUSDTUSDC:
            newToken = token1
            return newToken, token0
        elif token1 in WETHUSDTUSDC:
            newToken = token0
            return newToken,token1
        else:
            return token0,token1
        
    
    def confirmTokenNotAddedBefore(self,factory_contract,newToken,paired):
        poolAddress = factory_contract.functions.getPair(newToken,paired).call()
        return poolAddress
    
    def getReserves(self,connect,poolContract,WETHUSDTUSDC):
        reserve0,reserve1 = poolContract.functions.getReserves().call()[:2]
        token0 = connect.to_checksum_address(poolContract.functions.token0().call())
        if token0 in WETHUSDTUSDC:
            pooledNewtoken = reserve1
            pooledPairedToken = reserve0
            return pooledNewtoken,pooledPairedToken
        else:
            pooledNewtoken = reserve0
            pooledPairedToken = reserve1
            return pooledNewtoken,pooledPairedToken
        

    def notification(self,newTokenContract,newpairdContract,pooledNewtoken,pooledPairedToken,market):
        newTokenSymbol = newTokenContract.functions.symbol().call()
        newPairdSymbol = newpairdContract.functions.symbol().call()

        newTokenName = newTokenContract.functions.name().call()
        newPairedname = newpairdContract.functions.name().call()

        pooledNewtoken = pooledNewtoken / 10**newTokenContract.functions.decimals().call()
        pooledPairedToken = pooledPairedToken / 10**newpairdContract.functions.decimals().call()
        try:
            priceInPairedToken = pooledPairedToken/pooledNewtoken
            priceInPairedToken = "{:.10f}".format(priceInPairedToken)
            print(f'price of token in paiiredtoken is {priceInPairedToken}')
        except:
            priceInPairedToken = 0
            print(f'price of token in paiiredtoken is {priceInPairedToken}')

        try:
            coingecko = f"https://api.coingecko.com/api/v3/simple/token_price/arbitrum-one?contract_addresses={newpairdContract.address}&vs_currencies=usd"
            response = requests.get(coingecko)
            coin_data = response.json()
            pairedTokenPrice = coin_data[(newpairdContract.address).lower()]['usd']
        except:
            pairedTokenPrice = 0

        tokenPriceUSD = float(priceInPairedToken) * pairedTokenPrice

        try:
            newTokenSupply = (newTokenContract.functions.totalSupply().call()) / 10**newTokenContract.functions.decimals().call()
            FDV = tokenPriceUSD * newTokenSupply
            print('No Error')
        except:
            newTokenSupply ='Unknown'
            FDV = 'Unknown'
            print('Error Detected')

        photo_path = 'research.webp'
        link = f'https://arbiscan.io/token/{newTokenContract.address}'
        convert = "{:.11f}"
        formatPaired = float("{:.7f}".format(pooledPairedToken))
        format = "{:.7f}".format(pooledPairedToken)
        liquidityInfo = "🆕 🆕  New Pair Listed\n\n"\
                        f"🪙 {newTokenName} - {newTokenSymbol }/ {newPairdSymbol}\n\n"\
                        f"📜 Token address:{ newTokenContract.address}\n\n"\
                        f"💰 Price USD: ${convert.format(tokenPriceUSD)}\n"\
                        f"💰 Price: {priceInPairedToken} ({newPairdSymbol})\n"\
                        f"💰 FDV:${FDV}\n\n"\
                        f"💵 Total liquidity: ${2*round((pooledPairedToken*pairedTokenPrice),4)}\n"\
                        f"💵 Pooled ${newTokenSymbol}: {round(pooledNewtoken,2)}\n"\
                        f"💵 Pooled ${newPairdSymbol}: {format} (${(round((formatPaired*pairedTokenPrice),4))})\n\n"\
                        f"🤖 🤖 Bot Warnings :DYOR\n\n"\
                        f"⚠️ Liquidity {'Above $10000' if (2*round((pooledPairedToken*pairedTokenPrice),2)) > 10000 else 'Below $10000'} \n"\
                        f"⚠️  Buy / Sell Tax - Unknown\n\n"\
                        f'<a href="{link}">Arbiscan</a> | {"Trading On SushiSwap" if market == "Sushi" else "Trading On Camelot"}\n\n'\
                        f'🤖 Powered By JungleBot\n'
                        
        async def main():
            bot_token = #Your Telegram BotToken
            try:
                bot=telegram.Bot(bot_token)
            except:
                bot=telegram.Bot(bot_token)
            async with bot:
                await bot.send_photo(photo=open(photo_path,'rb'),caption=liquidityInfo,parse_mode=ParseMode.HTML,
                chat_id=-1002028741508) 
        if __name__!='__main__':
            asyncio.run(main())



        #963648721
    

    
    def activeBot(self):
        bot_token = # your telegram bottoken
        async def main():
            try:
                bot=telegram.Bot(bot_token)
            except:
                bot=telegram.Bot(bot_token)
            async with bot:
                await bot.send_message(text=f'Liquidity Updater Notification \n\nBOT_STATUS:ACTIVE',
                chat_id=963648721)
        if __name__!='__main__':
            asyncio.run(main())
        

        
