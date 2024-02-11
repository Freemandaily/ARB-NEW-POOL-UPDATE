from web3 import *
import time,os,sys,json
import updater_abi
from updater_class import liquidty_wizard

connect = Web3(Web3.HTTPProvider('https://arbitrum-mainnet.infura.io/v3/(YOUR INFURA API KEY)')) # TRADER_STORY RPC 

CAMELOT_FACTORY_CONTRACT = connect.eth.contract(address=connect.to_checksum_address(updater_abi.CAMELOT_FACTORY_ADDRESS),abi=updater_abi.CAMELOT_FACTORY_ABI)
SUSHI_FACTORY_CONTRACT = connect.eth.contract(address=connect.to_checksum_address(updater_abi.SUSHI_FACTORY_ADDRESS),abi=updater_abi.SUSHI_FACTORY_ABI)



WETH = connect.to_checksum_address(updater_abi.WETH)
USDT = connect.to_checksum_address(updater_abi.USDT)
USDC = connect.to_checksum_address(updater_abi.USDC)

WETHUSDTUSDC = [WETH,USDT,USDC]


processor = liquidty_wizard()
#Fetching The Pool lengthFrom The JsonFile
try:
    with open('camelotPoolLength','r') as lengthFile:
        length = json.load(lengthFile)
        camelotInitialPoolLength = length['poolLength']


except:
    with open('camelotPoolLength','w') as lengthFile:
        camelotInitialPoolLength = processor.getPoolLength(CAMELOT_FACTORY_CONTRACT)
        poolInfo = {'poolLength':camelotInitialPoolLength}
        json.dump(poolInfo,lengthFile)

#Fectching the poolLength from the json file
try:
    with open('sushiPoolLength','r') as lengthFile:
        length = json.load(lengthFile)
        sushiInitialPoolLength = length['poolLength']
except:
    with open('sushiPoolLength','w') as lengthFile:
        sushiInitialPoolLength = processor.getPoolLength(SUSHI_FACTORY_CONTRACT)
        poolInfo = {'poolLength':sushiInitialPoolLength}
        json.dump(poolInfo,lengthFile)

inactive = 0
null = 'None'
fetching = True
while fetching:
    inactive +=1
    print('Fetching Pools')
    camelotPoolAddresses,camelotInitialPoolLength = processor.scanFactory(CAMELOT_FACTORY_CONTRACT,camelotInitialPoolLength)
  
    sushiPoolAddresses,sushiInitialPoolLength = processor.scanFactory(SUSHI_FACTORY_CONTRACT,sushiInitialPoolLength)

    if  camelotPoolAddresses != null:
        inactive = 0

        print('yes i am here')
        for poolAddress in camelotPoolAddresses :
            poolContract = connect.eth.contract(address=connect.to_checksum_address(poolAddress),abi=updater_abi.CAMELOT_POOL_ABI)

            newToken,pairedToken = processor.pooledTokens(connect,poolContract,WETHUSDTUSDC)
            print(newToken,pairedToken)
            pairsTokenList = [pair for pair in WETHUSDTUSDC if pair != pairedToken]
            
            #Checking That This Token Has Not Been Live With Other Pairs
            truthPool = []
            for paired in pairsTokenList:
                poolAddress = processor.confirmTokenNotAddedBefore(CAMELOT_FACTORY_CONTRACT,newToken,paired)
                if poolAddress == '0x0000000000000000000000000000000000000000':
                    truthPool.append('yes')
                    
                    print(len(truthPool))
                    if len(truthPool) == 2 :
                        pooledNewtoken,pooledPairedToken = processor.getReserves(connect,poolContract,WETHUSDTUSDC)
                        print(f'Camelot Pooled Token:{pooledNewtoken}')

                        newTokenContract = connect.eth.contract(address=connect.to_checksum_address(newToken),abi=updater_abi.BASIC_TOKEN_ABI)
                        newpairdContract = connect.eth.contract(address=connect.to_checksum_address(pairedToken),abi=updater_abi.BASIC_TOKEN_ABI)

                        print('Sending Notification For Camelot')
                        processor.notification(newTokenContract,newpairdContract,pooledNewtoken,pooledPairedToken,'Camelot')
                        #time.sleep(1234)
        
        #Updating the Camelot json file
        with open('camelotPoolLength','w') as lengthFile:
            poolInfo = {'poolLength':camelotInitialPoolLength}
            json.dump(poolInfo,lengthFile)

    #For Sushi              
    if sushiPoolAddresses != null:
        inactive =  0
        for poolAddress in sushiPoolAddresses :
            poolContract = connect.eth.contract(address=connect.to_checksum_address(poolAddress),abi=updater_abi.SUSHI_POOL_ABI)

            newToken,pairedToken = processor.pooledTokens(connect,poolContract,WETHUSDTUSDC)
            pairsTokenList = [pair for pair in WETHUSDTUSDC if pair != pairedToken]
            
            #Checking That This Token Has Not Been Live With Other Pairs
            truthPool = []
            for paired in pairsTokenList:
                print('Checking for available Liquidity From Sushi Pool')
                poolAddress = processor.confirmTokenNotAddedBefore(SUSHI_FACTORY_CONTRACT,newToken,paired)
                if poolAddress == '0x0000000000000000000000000000000000000000':
                    truthPool.append('yes')
                    
                
                    if len(truthPool) == 2 :
                        pooledNewtoken,pooledPairedToken = processor.getReserves(connect,poolContract,WETHUSDTUSDC)
                        print(f'Sushiswap Pooled Token: {pooledNewtoken}')

                        newTokenContract = connect.eth.contract(address=connect.to_checksum_address(newToken),abi=updater_abi.BASIC_TOKEN_ABI)
                        newpairdContract = connect.eth.contract(address=connect.to_checksum_address(pairedToken),abi=updater_abi.BASIC_TOKEN_ABI)

                        print('Sending The Notifiction For Sushi')
                        processor.notification(newTokenContract,newpairdContract,pooledNewtoken,pooledPairedToken,'Sushi')


        #Updating the json file for sushi swap
        with open('sushiPoolLength','w') as lengthFile:
            poolInfo = {'poolLength':sushiInitialPoolLength}
            json.dump(poolInfo,lengthFile)
    
    #Time For The Next Checking
    #Giving Noification if there is new pool token in 30 minutes
    print('Waiting For 3 Minute For An Update')
    if inactive == 10:
        processor.activeBot()
        inactive = 0
    time.sleep(3*60)
                    

