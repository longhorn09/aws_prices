import re                           # for regular expression, to parse out instance size from instanceType attribute
import json                         # need this library to interact with JSON data structures
import urllib.request               # need this library to open up remote website
import xlsxwriter                   # pip3 install xlsxwriter   , xlwt doesn't support .xlsx
import sys
from operator import itemgetter, attrgetter # https://docs.python.org/3/howto/sorting.html

class SKUClass:
    def __init__(self,pFam,pSize, pRegionCode, pSKU, pOS,pUsageType):
        self.instanceFamily = pFam
        self.instanceSize = pSize
        self.regionCode = pRegionCode
        self.sku = pSKU
        self.os = pOS
        self.rateCode = ''
        self.price = 0.0
        self.usageType = pUsageType
        self.price1yrNoUpfront = 0.0
        self.rateCode2 = ''
    
#########################################################################################
# offer index file: https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json
#########################################################################################
class AWSPricing:
    ROOT_URL = 'https://pricing.us-east-1.amazonaws.com'

    region_map={
        # Americas
        "CMH": ("us-east-2", "US East (Ohio)"),
        "IAD": ("us-east-1","US East (N. Virginia)"),
        "PDX": ("us-west-2","US West (Oregon)"),
        "SFO": ("us-west-1","US West (N. California)"),

        ##### us-west-2-lax-1a, us-west-2-lax-1b
        # doesn't seem to work
        #"LAX": ("us-west-2-lax-1a","US West (Los Angeles)"), # https://aws.amazon.com/blogs/aws/announcing-a-second-local-zone-in-los-angeles/

        # Canada
        "YYZ": ("ca-central-1","Canada (Central)"),     # Toronto Pearson International

        # LATAM
        "GRU": ("sa-east-1","South America (Sao Paulo)"),

        # ME / Africa
        "BAH": ("me-south-1","Middle East (Bahrain)"),
        "CPT": ("af-south-1","Africa (Cape Town)"),
        # APAC
        "HKG": ("ap-east-1","Asia Pacific (Hong Kong)"),
        "BOM": ("ap-south-1","Asia Pacific (Mumbai)"),
        "ITM": ("ap-northeast-3","Asia Pacific (Osaka-Local)"),
        "ICN": ("ap-northeast-2","Asia Pacific (Seoul)"),
        "SIN": ("ap-southeast-1","Asia Pacific (Singapore)"),
        "SYD": ("ap-southeast-2","Asia Pacific (Sydney)"),
        "NRT": ("ap-northeast-1","Asia Pacific (Tokyo)"),
        # EU        
        "FRA": ("eu-central-1","EU (Frankfurt)"),
        "DUB": ("eu-west-1", "EU (Ireland)"),
        "LHR": ("eu-west-2","EU (London)"),
        "MXP": ("eu-south-1","EU (Milan)"),
        "CDG": ("eu-west-3","EU (Paris)"),
        "ARN": ("eu-north-1","EU (Stockholm)")

        
    }

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
        ## end of variable declaration

        url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'          # simply lookup "AmazonEC2"   , then "currentSavingsPlanIndexUrl"

        contents  = urllib.request.urlopen(url).read() 
        myJSON = json.loads(contents)
        retvalue = (myJSON["offers"]["AmazonEC2"]["currentSavingsPlanIndexUrl"]).strip()    #ie. https://pricing.us-east-1.amazonaws.com/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/region_index.json

        return retvalue

    # ie. for IAD this returns "us-east-1"
    def getAWSRegionFromCode(self, pRegionCode):
        return self.region_map.get(pRegionCode,(None,None))[0]
    
    # ie. for IAD this returns "US East (N. Virginia)"
    def getAWSLocationFromCode(self,pRegionCode):
        return self.region_map.get(pRegionCode,(None,None))[1]

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
    def getSKUListLocal(self, pRegionCodeCSV):
        myJSON = None
        counter = None
        instanceType = None
        my_list = []
        url = None
        doLocal = None    

        ############################################    
        # [FASTER, stale  ] Toggle doLocal to True if JSON already saved locally as index_aws_ec2.json, can use doSaveJSONLocal() for initial save
        # [SLOWER, fresher] Toggle doLocal to False to pull from AWS site - this is a 1GB+ sized read
        ############################################
        #doLocal = False  # True for Dev , false for Prod
        doLocal = True  #  already have a 1.6GB+ JSON saved locally as index_aws_ec2.json

        if (doLocal):
            # this is a 1.3 GB file - may take time
            with open('index_aws_ec2.json') as json_file: 
                myJSON = json.load(json_file)   # note: json.load() for local file instead of json.loads() 
        elif (doLocal == False):
            url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'
            contents  = urllib.request.urlopen(url).read() 
            myJSON = json.loads(contents)
            
            url = self.ROOT_URL + myJSON["offers"]["AmazonEC2"]["currentVersionUrl"]
            contents  = urllib.request.urlopen(url).read() 
            myJSON = json.loads(contents)
            
        regionArr = pRegionCodeCSV.split(",")

        for x in range(len(regionArr)):         
            #print(regionArr[x] + ': ' + self.getAWSLocationFromCode(regionArr[x]))
            for key,value in myJSON["products"].items():    
                # regex pattern for ["attributes"]["usagetype"] can be:
                # EU-EC2SP:r4.1yrAllUpfront
                # EU-BoxUsage:m5.8xlarge
                # EUW2-BoxUsage:m5d.xlarge
                # BoxUsage:m5d.xlarge
                pattern = "^([A-Z0-9\-]+)?BoxUsage:.+$"      # make sure BoxUsage, not UnusedBox etc
                try:
                    if (value["productFamily"] == "Compute Instance" and value["attributes"]["servicecode"] == "AmazonEC2"
                        and (value["attributes"]["operatingSystem"] == "Linux"  or value["attributes"]["operatingSystem"] == "RHEL"  or value["attributes"]["operatingSystem"] == "Windows")
                        and value["attributes"]["preInstalledSw"] == "NA"
                        #and value["attributes"]["instanceFamily"] == "General purpose"
                        and value["attributes"]["locationType"] == "AWS Region"
                        and value["attributes"]["tenancy"] == "Shared"
                        and value["attributes"]["location"] == self.getAWSLocationFromCode(regionArr[x])
                        and re.match(pattern,value["attributes"]["usagetype"])):
                        #print("yCount: " + self.getAWSLocationFromCode(regionArr[x]) + ", sku: " + value["sku"] + ", usageType:" + value["attributes"]["usagetype"])
                        pattern = "^(.+)\.([0-9A-Za-z]+)$"
                        if ("instanceType" in value["attributes"] and re.match(pattern,value["attributes"]["instanceType"])):
                            m = re.search(pattern, value["attributes"]["instanceType"])
                            #if (m.group(2) == "small"):        #not all instanceFamily have size small
                                #print (key + ": " + m.group(0))                                                
                            #print(m.group(1)  + " " + regionArr[x] + " " + key + " " + value["attributes"]["operatingSystem"])
                            my_list.append( SKUClass(m.group(1)
                                                    , m.group(2)   
                                                    , regionArr[x] #pRegionCode
                                                    , key  
                                                    , value["attributes"]["operatingSystem"]
                                                    , value["attributes"]["usagetype"])
                                        )
                except: 
                    print(key + ': no productFamily')
        my_list = sorted(my_list, key=attrgetter('regionCode','instanceFamily','instanceSize'))

        return my_list

    ############################################################################
    # Description: can handle multiple regions based on provided CSV list
    # @pArg1 - this is a CSV list of regions by 3 letter airport code
    # @pArg2 - this is the list Array of SKUClass objects
    ############################################################################
    #  JSON structure   - https://jsoneditoronline.org/
    #  -products
    #  -terms  
    #   └savingsPlan
    #    └ sku
    #    └ rates
    #      └ rateCode                   "RQRC4CUNT9HUG9WC.TBV6C3VKSXKFHHSC"
    #      └ discountedRate
    #        └ price                    "0.0679"
    ############################################################################
    def getSavingsPlanPrices2(self,pArg1, pArg2):
        contents = None
        myJSON = None
        doLocal = None
        spURL = None
        regionURL = None
        productSku = None
        productSku1yrNoUpfront = None

        # END VARIABLE DECLARATION 

        spURL = self.getOfferIndexURL()     # gets the current savings plan URL, which is an index of all the regions' savings plan URLs
        doLocal = False                      # set to false for production        

        for regionSplitLoop in range(len(pArg1.strip().split(","))):
            productSku = None
            productSku1yrNoUpfront = None
            regionURL  = self.getSavingsPlanPriceListUrlForRegion(pArg1.strip().split(",")[regionSplitLoop], spURL)
            
            if (doLocal == False):
                print('[' + pArg1.strip().split(",")[regionSplitLoop] + '] ' + regionURL)
                contents  = urllib.request.urlopen(regionURL).read() 
                myJSON = json.loads(contents)          # for production - use actual web url (slower)                    
            elif (doLocal == True):
                with open('CMH.json') as json_file:         
                    myJSON = json.load(json_file)
            
            # this loop to get the sku that corresponds with 3yr All Upfront ComputeSavingsPlan
            # later also look for 1yr No upfront Compute Savings plan
            for item in myJSON["products"]:    
                if (item["usageType"] == "ComputeSP:3yrAllUpfront" and item["productFamily"] == "ComputeSavingsPlans"):
                    productSku = item["sku"]
                elif (item["usageType"] == "ComputeSP:1yrNoUpfront" and item["productFamily"] == "ComputeSavingsPlans"):
                    productSku1yrNoUpfront =  item["sku"] 
                if (productSku is not None and productSku1yrNoUpfront is not None ):
                    #print ('productSku1yrNoUpfront: ' + productSku1yrNoUpfront)
                    break

            # now get the actual rates in the "terms" section of the JSON
            for item in myJSON["terms"]["savingsPlan"]:
                if (item["sku"] ==  productSku):
                    foundRateList = item["rates"]                    
                    break

            # find the price by rateCode - ie. "RQRC4CUNT9HUG9WC.TBV6C3VKSXKFHHSC"
            for x in range(len(pArg2)):
                #print("getSavingsPlanPrices2: [" + pArg2[x].regionCode + "]: " + pArg2[x].sku + ", os: " + pArg2[x].os + ", " + pArg2[x].instanceFamily + "." + pArg2[x].instanceSize)
                for item in foundRateList:
                    if (item['rateCode'] == productSku + '.' + pArg2[x].sku):
                        pArg2[x].price = item['discountedRate']['price']
                        pArg2[x].rateCode = item['rateCode']
                        #print(item['rateCode'] + ": " + pArg2[x].price + ", " + pArg2[x].instanceFamily + ", " + pArg2[x].instanceSize+ ", " + pArg2[x].os)
                        break
            
            ###  repeat same loops but for 1yrNoUpfront savings plan
            for item in myJSON["terms"]["savingsPlan"]:
                if (item["sku"] ==  productSku1yrNoUpfront):
                    foundRateList = item["rates"]                    
                    break

            # find the price by rateCode - ie. "RQRC4CUNT9HUG9WC.TBV6C3VKSXKFHHSC"
            for x in range(len(pArg2)):
                for item in foundRateList:
                    if (item['rateCode'] == productSku1yrNoUpfront + '.' + pArg2[x].sku):
                        pArg2[x].price1yrNoUpfront = item['discountedRate']['price']
                        pArg2[x].rateCode2 = item['rateCode']
                        break

        return pArg2

    ##############################################################
    #  @pArg1 the list of SKUClass objects
    ##############################################################
    def doWriteExcel(self,pArg1):
        counter = 2
        blankCount = 0

        try:
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
            sheet1.write_string('H1','usageType')
            sheet1.write_string('I1','3yrAllUpfront')
            sheet1.write_string('J1','1yrNoUpfront')
            sheet1.write_string('K1','rateCode1yrNoUpfront')

            sheet1.set_column('B:C',14)
            sheet1.set_column('G:G',43)
            #print("len(pArg1): " + len(pArg1))
            for x in range(len(pArg1)):
                if (float(pArg1[x].price) > 0):
                    sheet1.write_string('A' + str(counter), pArg1[x].regionCode)
                    sheet1.write_string('B' + str(counter), self.getAWSRegionFromCode(pArg1[x].regionCode))
                    sheet1.write_string('C' + str(counter), self.getAWSLocationFromCode(pArg1[x].regionCode))
                    sheet1.write_string('D' + str(counter), pArg1[x].os)
                    sheet1.write_string('E' + str(counter), pArg1[x].instanceFamily)
                    sheet1.write_string('F' + str(counter), pArg1[x].instanceSize)
                    sheet1.write_string('G' + str(counter), pArg1[x].rateCode)
                    sheet1.write_string('H' + str(counter), pArg1[x].usageType)
                    sheet1.write_number('I' + str(counter), float(pArg1[x].price),money)
                    sheet1.write_number('J' + str(counter), float(pArg1[x].price1yrNoUpfront),money) #float(pArg1[x].price1yrNoUpfront),money)
                    sheet1.write_string('K' + str(counter), pArg1[x].rateCode2)
                    #print(pArg1[x].regionCode + ', ' + pArg1[x].os + ', ' +  pArg1[x].instanceFamily + ', ' + pArg1[x].instanceSize + ', 3yr: ' + pArg1[x].price + ', 1yr: ' + pArg1[x].price1yrNoUpfront)
                    counter += 1       # this increments the Excel output row 
                else:
                    blankCount += 1
            print('blankCount (https://github.com/longhorn09/aws_prices/issues/1): ' + str(blankCount))
            book.close()    # close the excel file
        except:
            print("doWriteExcel(): Error trying to write to Excel",sys.exc_info()[0],"occurred.")
    #######################################################
    # Run this once to create a local copy of large 1.3GB JSON file for local development and testing purposes
    #######################################################
    def doSaveJSONLocal(self):
        url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'

        try:
            contents  = urllib.request.urlopen(url).read() 
            myJSON = json.loads(contents)

            url = self.ROOT_URL + myJSON["offers"]["AmazonEC2"]["currentVersionUrl"]
            #print(url)
            contents  = urllib.request.urlopen(url).read() 
            myJSON = json.loads(contents)
        except:            
            print("doSaveJSONLocal(): Error reading JSON From AWS",sys.exc_info()[0],"occurred.")

        try:
            with open('index_aws_ec2.json','w') as outfile:
                json.dump(myJSON, outfile)
                outfile.close()
        except:
            print("doSaveJSONLocal(): Error trying to write Excel file",sys.exc_info()[0],"occurred.")

############################################
# MAIN CODE EXECUTION BEGIN
############################################
if __name__ == '__main__':
    listArr = []
    regionURL = None

    # regionsArg expects a CSV list of 3 letter airport region codes
    # tweak as necessary for the regions of interest
    # issues with ITM and BOM?
    #regionsArg = "CMH,LHR,FRA,IAD,PDX,SIN,GRU,NRT,DUB,SYD,CDG,ICN,SFO"
    regionsArg = ""
    regionsArg = regionsArg + "CMH" # US East (Ohio)
    regionsArg = regionsArg + ",LHR" # EU (London)
    regionsArg = regionsArg + ",FRA" # EU (Frankfurt)
    regionsArg = regionsArg + ",IAD" # US East (N. Virginia)
    regionsArg = regionsArg + ",PDX" # US West (Oregon)
    regionsArg = regionsArg + ",SIN" # Asia Pacific (Singapore)
    regionsArg = regionsArg + ",GRU" # South America (Sao Paulo)
    regionsArg = regionsArg + ",NRT" # Asia Pacific (Tokyo)
    regionsArg = regionsArg + ",DUB" # EU (Ireland)
    regionsArg = regionsArg + ",SYD" # Asia Pacific (Sydney)
    regionsArg = regionsArg + ",CDG" # EU (Paris)
    regionsArg = regionsArg + ",ICN" # Asia Pacific (Seoul)
    regionsArg = regionsArg + ",SFO" # US West (N. California)
    regionsArg = regionsArg + ",CPT" # Africa (Cape Town)
    regionsArg = regionsArg + ",MXP" # EU (Milan)
    regionsArg = regionsArg + ",BAH" # Middle East (Bahrain)
    regionsArg = regionsArg + ",ARN" # EU (Stockholm)
    regionsArg = regionsArg + ",HKG" # Asia Pacific (Hong Kong)
    regionsArg = regionsArg + ",YYZ" # Canada (Central)
    #issues with LAX & ITM , ie. Local regions    

    myObj = AWSPricing()                            # object instantiation

    # do this once to save a 1GB+ JSON locally for local development, and comment all lines of code after myObj.doSaveJSONLocal()
    # for faster performance, just copy/paste the appropriate URL into your browser and save off/rename the JSON retrieved to index_aws_ec2.json
    # myObj.doSaveJSONLocal()    
    
    listArr = myObj.getSKUListLocal(regionsArg)      # loops thru the big 1GB+ JSON, to get the appropriate product SKUs for a region    
    
    listArr = myObj.getSavingsPlanPrices2(regionsArg, listArr)    
    myObj.doWriteExcel(listArr)
    

