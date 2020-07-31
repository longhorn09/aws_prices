from datetime import datetime, date,time
from datetime import timezone       # use python3
import re                           # for regular expression, to parse out instance size from instanceType attribute
#import calendar                     # need this module for last day of month
import json                         # need this library to interact with JSON data structures
import urllib.request               # need this library to open up remote website (ie. controltower)
import xlsxwriter                   # pip3 install xlsxwriter   , xlwt doesn't support .xlsx
from operator import itemgetter, attrgetter # https://docs.python.org/3/howto/sorting.html
#from dateutil.relativedelta import relativedelta    # pip3 install python-dateutil


class SKUClass:
    def __init__(self,pFam,pSize, pRegionCode, pSKU):
        self.instanceFamily = pFam
        self.instanceSize = pSize
        self.regionCode = pRegionCode
        self.sku = pSKU
        #self.
    
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
    # for use with ["attributes"]["location"] in SKU JSON
    #######################################################################
    def getAWSLocationFromCode(self,pArg1):
        retvalue = None
        if pArg1 == 'CMH':  # Columbus, OH
            retvalue = 'US East (Ohio)'                
        elif pArg1 == "DUB":    # Dublin, IE
            retvalue = 'EU (Ireland)'
        elif pArg1 == "FRA":    # Frankfurt, GR
            retvalue = 'EU (Frankfurt)'
        elif pArg1 == "GRU":    # Sao Paulo, BR
            retvalue = 'South America (Sao Paulo)'    
        elif pArg1 == "IAD":
            retvalue = "US East (N. Virginia)"
        elif pArg1 == "LHR":
            retvalue = 'EU (London)'    #'eu-west-2'
        elif pArg1 == "NRT":    
            retvalue = 'Asia Pacific (Tokyo)'   #'ap-northeast-1'
        elif pArg1 == "PDX":
            retvalue = 'US West (Oregon)'   #'us-west-2'
        elif pArg1 == "SIN":
            retvalue = 'Asia Pacific (Singapore)'   #'ap-southeast-1'
        elif pArg1 == "SYD":
            retvalue = 'Asia Pacific (Sydney)'  #'ap-southeast-2'        
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
        #     BoxUsage (regular OD) vs.
        #     UnusedBox
        # vs. DedicatedUsage
        # vs. UnusedDed
        
        return retvalue
   
    #######################################################################
    # URL lookup for region SP version  Url
    #######################################################################
    def getSKUListLocal(self, pRegionCode):
        myJSON = None
        counter = None
        instanceType = None
        my_list = []

        pattern = "^(.+)\.([0-9A-Za-z]+)"
        with open('index_aws_ec2.json') as json_file:
            myJSON = json.load(json_file)   # note: json.load() for local file instead of json.loads() 
        #print(len(myJSON["products"]))
        counter = 0
        #print(myJSON["products"])
        #print(myJSON["products"][0]["sku"])
        for key,value in myJSON["products"].items(): #range(len(myJSON["products"])):
            if (value["productFamily"] == "Compute Instance" and value["attributes"]["servicecode"] == "AmazonEC2"
                and value["attributes"]["operatingSystem"] == "Linux" # or value["attributes"]["operatingSystem"] == "RHEL")
                and value["attributes"]["preInstalledSw"] == "NA"
                and value["attributes"]["instanceFamily"] == "General purpose"
                and value["attributes"]["locationType"] == "AWS Region"
                and value["attributes"]["tenancy"] == "Shared"
                and value["attributes"]["location"] == self.getAWSLocationFromCode(pRegionCode)):

                if ("instanceType" in value["attributes"] and re.match(pattern,value["attributes"]["instanceType"])):
                    m = re.search(pattern, value["attributes"]["instanceType"])
                    #if (m.group(2) == "small"):        #not all instanceFamily have size small
                        #print (key + ": " + m.group(0))
                    my_list.append( SKUClass(m.group(1),m.group(2)   ,pRegionCode, key         )                )
                        #counter = counter + 1            
                
            #if (counter > 10):
            #    break
        #my_list.sort()
        #sorted(my_list, key=lambda SKUClass: SKUClass.instanceFamily)
        my_list = sorted(my_list, key=attrgetter('instanceFamily','instanceSize'))
        for x in range(len(my_list)):
            print(my_list[x].sku + ", " + my_list[x].instanceFamily + "." + my_list[x].instanceSize)



############################################
# MAIN CODE EXECUTION BEGIN
############################################
if __name__ == '__main__':
    regionURL = None
    
    myObj = AWSPricing()
    spURL = myObj.getOfferIndexURL()
    
    
    #myObj.getSavingsPlanPriceListForRegion('IAD', spURL)

    myObj.getSKUListLocal("LHR")
    #print(myObj.getAWSRegionFromCode('DUB'))
