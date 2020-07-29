from datetime import datetime, date,time
from datetime import timezone       # use python3
import calendar                     # need this module for last day of month
import json                         # need this library to interact with JSON data structures
import urllib.request               # need this library to open up remote website (ie. controltower)
import xlsxwriter                   # pip3 install xlsxwriter   , xlwt doesn't support .xlsx
from dateutil.relativedelta import relativedelta    # pip3 install python-dateutil

#########################################################################################
# offer index file: https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json
#########################################################################################

class AWSPricing:
    ROOT_URL = 'https://pricing.us-east-1.amazonaws.com'
    def __init__(self):
        super().__init__()
    
    def getSavingsPlanURL(self):
        return "ok"

    #######################################################################
    # first check the offer index file to get the paths to the savings plan index Url
    #######################################################################
    def getOfferIndexURL(self):
        retvalue = None
        url = None
        contents = None
        myJSON = None

        url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'
        contents  = urllib.request.urlopen(url).read() 
        myJSON = json.loads(contents)
        retvalue = (myJSON["offers"]["AmazonEC2"]["currentSavingsPlanIndexUrl"]).strip()    #ie. https://pricing.us-east-1.amazonaws.com/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/region_index.json

        #print(retvalue)
        return retvalue

    #######################################################################
    # simple case statement for region lookup
    # if missing code, append to the elif and submit pull request
    #######################################################################
    def getAWSRegionFromCode(self, pArg1):
        retvalue = None
        if pArg1 == 'CMH':  # Columbus, OH
            retvalue = 'us-east-2'                
        elif pArg1 == "DUB":    # Dublin, IE
            retvalue = 'eu-west-1'
        elif pArg1 == "FRA":    # Frankfurt, GR
            retvalue = 'eu-central-1'
        elif pArg1 == "GRU":    # Sao Paulo, BR
            retvalue = 'sa-east-1'    
        elif pArg1 == "IAD":
            retvalue = "us-east-1"
        elif pArg1 == "LHR":
            retvalue = 'eu-west-2'
        elif pArg1 == "NRT":    
            retvalue = 'ap-northeast-1'
        elif pArg1 == "PDX":
            retvalue = 'us-west-2'
        elif pArg1 == "SIN":
            retvalue = 'ap-southeast-1'
        elif pArg1 == "SYD":
            retvalue = 'ap-southeast-2'        
        return retvalue

    #######################################################################
    # URL lookup for region SP version  Url
    #######################################################################
    def getSavingsPlanPriceListForRegion(self, pArg1, pArg2):
        url = None 
        contents = None
        myJSON = None
        retvalue = None
        versionUrlPath = None

        regionId = self.getAWSRegionFromCode(pArg1) # convert 3 letter airport code IAD to 'us-east-1'        
        url = self.ROOT_URL + pArg2        
        contents  = urllib.request.urlopen(url).read() 
        myJSON = json.loads(contents)

        for x in range(len(myJSON["regions"])):
            if ((myJSON["regions"][x]["regionCode"]).strip() == regionId):                
                versionUrlPath = myJSON["regions"][x]["versionUrl"]
                break   # get outta the for loop

        
        url = self.ROOT_URL + versionUrlPath
        print(url)
        contents  = urllib.request.urlopen(url).read() 
        myJSON = json.loads(contents)

        # Tenancy: Shared, Dedicated Instance, Dedicated Host
        # 3Y all upfront
        #     BoxUsage vs.
        #     UnusedBox
        # vs. DedicatedUsage
        # vs. UnusedDed
        
        return retvalue
   


############################################
# MAIN CODE EXECUTION BEGIN
############################################
if __name__ == '__main__':
    regionURL = None
    
    myObj = AWSPricing()
    spURL = myObj.getOfferIndexURL()
    
    
    myObj.getSavingsPlanPriceListForRegion('IAD', spURL)
    #print(myObj.getAWSRegionFromCode('DUB'))
