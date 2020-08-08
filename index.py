import re                           # for regular expression, to parse out instance size from instanceType attribute
import json                         # need this library to interact with JSON data structures
import urllib.request               # need this library to open up remote website (ie. controltower)
import xlsxwriter                   # pip3 install xlsxwriter   , xlwt doesn't support .xlsx
from operator import itemgetter, attrgetter # https://docs.python.org/3/howto/sorting.html

class SKUClass:
    def __init__(self,pFam,pSize, pRegionCode, pSKU, pOS):
        self.instanceFamily = pFam
        self.instanceSize = pSize
        self.regionCode = pRegionCode
        self.sku = pSKU
        self.os = pOS
    
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

        
        # simply lookup "AmazonEC2"   , then "currentSavingsPlanIndexUrl"
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
    # URL lookup for region SP version Url
    # @pArg1 - the 3 letter region to lookup (ie. the airport code)
    # @pArg2 - URL to fetch savings plan JSON
    #######################################################################
    def getSavingsPlanPriceListUrlForRegion(self, pArg1, pArg2):
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
        retvalue = url
        
        return retvalue
   
    #######################################################################
    # URL lookup for region SP version  Url
    #######################################################################
    def getSKUListLocal(self, pRegionCode):
        myJSON = None
        counter = None
        instanceType = None
        my_list = []
        url = None
        doLocal = None
        #productSku = None        

        doLocal = True  # for local development, this is faster but may be outdated. for production, set this to false

        if (doLocal):
            # this is a 1.3 GB file - may take time
            with open('index_aws_ec2.json') as json_file: 
                myJSON = json.load(json_file)   # note: json.load() for local file instead of json.loads() 
        elif (doLocal == False):
            # ["offers"]["AmazonEC2"]["currentVersionUrl"]
            url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'
            contents  = urllib.request.urlopen(url).read() 
            myJSON = json.loads(contents)
            retvalue = (myJSON["offers"]["AmazonEC2"]["currentVersionUrl"]).strip()
            
        counter = 0

        for key,value in myJSON["products"].items():    
            pattern = "^[A-Z]+[0-9]+\-BoxUsage.+$"      # make sure BoxUsage, not UnusedBox etc
            if (value["productFamily"] == "Compute Instance" and value["attributes"]["servicecode"] == "AmazonEC2"
                and (value["attributes"]["operatingSystem"] == "Linux"  or value["attributes"]["operatingSystem"] == "RHEL"  or value["attributes"]["operatingSystem"] == "Windows")
                and value["attributes"]["preInstalledSw"] == "NA"
                and value["attributes"]["instanceFamily"] == "General purpose"
                and value["attributes"]["locationType"] == "AWS Region"
                and value["attributes"]["tenancy"] == "Shared"
                ###########################################################
                # right now for development - this is CMH for pRegionCode
                ###########################################################
                and value["attributes"]["location"] == self.getAWSLocationFromCode(pRegionCode)
                and re.match(pattern,value["attributes"]["usagetype"])):

                pattern = "^(.+)\.([0-9A-Za-z]+)$"
                if ("instanceType" in value["attributes"] and re.match(pattern,value["attributes"]["instanceType"])):
                    m = re.search(pattern, value["attributes"]["instanceType"])
                    #if (m.group(2) == "small"):        #not all instanceFamily have size small
                        #print (key + ": " + m.group(0))
                    my_list.append( SKUClass(m.group(1)
                                            , m.group(2)   
                                            , pRegionCode
                                            , key  
                                            , value["attributes"]["operatingSystem"]))
        
        my_list = sorted(my_list, key=attrgetter('instanceFamily','instanceSize'))

        return my_list

    ##############################################################
    # @pArg1 -  example: https://pricing.us-east-1.amazonaws.com/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/20200806153551/us-east-2/index.json
    # @pArg2 -  list of SKUClass
    #    
    #  JSON structure   - https://jsoneditoronline.org/
    #  -products
    #  -terms  
    #   └savingsPlan
    #    └ sku
    #    └ rates
    #      └ rateCode                   "RQRC4CUNT9HUG9WC.TBV6C3VKSXKFHHSC"
    #      └ discountedRate
    #        └ price                    "0.0679"
    ##############################################################
    def getSavingsPlanPrices(self,pArg1, pArg2):
        # BEGIN VARIABLE DECLARATION 
        contents = None
        url = None
        myJSON = None
        doLocal = None
        # END VARIABLE DECLARATION 

        doLocal = False          # set to false for production

        url = pArg1

        if (doLocal == False):
            contents  = urllib.request.urlopen(url).read() 
            myJSON = json.loads(contents)          # for production - use actual web url (slower)        
        elif (doLocal == True):
            with open('CMH.json') as json_file: 
                myJSON = json.load(json_file)
        
        # this loop to get the sku that corresponds with 3yr All Upfront ComputeSavingsPlan
        for item in myJSON["products"]:    
            if (item["usageType"] == "ComputeSP:3yrAllUpfront" and item["productFamily"] == "ComputeSavingsPlans"):
                productSku = item["sku"]
                break

        # now get the actual rates in the "terms" section of the JSON
        for item in myJSON["terms"]["savingsPlan"]:
            if (item["sku"] ==  productSku):
                foundRateList = item["rates"]                    
                break;

        # find the price by rateCode - ie. "RQRC4CUNT9HUG9WC.TBV6C3VKSXKFHHSC"
        for x in range(len(pArg2)):
            #print(pArg2[x].sku)
            for item in foundRateList:
                if (item['rateCode'] == productSku + '.' + pArg2[x].sku):
                    pArg2[x].price = item['discountedRate']['price']
                    pArg2[x].rateCode = item['rateCode']
                    #print(item['rateCode'] + ": " + pArg2[x].price + ", " + pArg2[x].instanceFamily + ", " + pArg2[x].instanceSize+ ", " + pArg2[x].os)
                    break
        return pArg2

    ##############################################################
    #  @pArg1 the list of SKUClass objects
    ##############################################################
    def doWriteExcel(self,pArg1):
        counter = 2
        book = xlsxwriter.Workbook('sp_prices.xlsx')
        sheet1 = book.add_worksheet('prices')


        money = book.add_format({'num_format': '#,##0.0000'})   # https://xlsxwriter.readthedocs.io/tutorial02.html
        #####################################
        # write headers in row 1
        #####################################
        sheet1.write_string('A1','RegionCode')
        sheet1.write_string('B1','Region')
        sheet1.write_string('C1','Location')
        sheet1.write_string('D1','OS')
        sheet1.write_string('E1','InstanceFamily')
        sheet1.write_string('F1','Size')
        sheet1.write_string('G1','rateCode')
        sheet1.write_string('H1','price')

        sheet1.set_column('B:C',14)
        sheet1.set_column('G:G',43)

        for x in range(len(pArg1)):
            sheet1.write_string('A' + str(counter), pArg1[x].regionCode)
            sheet1.write_string('B' + str(counter), self.getAWSRegionFromCode(pArg1[x].regionCode))
            sheet1.write_string('C' + str(counter), self.getAWSLocationFromCode(pArg1[x].regionCode))
            sheet1.write_string('D' + str(counter), pArg1[x].os)
            sheet1.write_string('E' + str(counter), pArg1[x].instanceFamily)
            sheet1.write_string('F' + str(counter), pArg1[x].instanceSize)
            sheet1.write_string('G' + str(counter), pArg1[x].rateCode)
            sheet1.write_string('H' + str(counter), pArg1[x].price,money)
            counter = counter + 1

        book.close()    # close the excel file

############################################
# MAIN CODE EXECUTION BEGIN
############################################
if __name__ == '__main__':
    listArr = []
    regionURL = None
    
    myObj = AWSPricing()
    spURL = myObj.getOfferIndexURL()
    
    listArr = myObj.getSKUListLocal("CMH")      # loop thru the big 1.3GB JSON, to get the appropriate product SKUs for a region
    regionURL = myObj.getSavingsPlanPriceListUrlForRegion('CMH', spURL)    # this just gets the appropriate savings plan url for a region
    listArr = myObj.getSavingsPlanPrices(regionURL, listArr)

    myObj.doWriteExcel(listArr)


    
