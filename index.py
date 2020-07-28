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
    def __init__(self):
        super().__init__()
    
    def getSavingsPlanURL(self):
        return "ok"

    #######################################################################
    # first check the offer index file to get the paths to the savings plan index Url
    #######################################################################
    def getOfferIndexURL(self):
        url = None
        contents = None
        myJSON = None
        url = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json'
        contents  = urllib.request.urlopen(url).read() 
        myJSON = json.loads(contents)
        print(myJSON["offers"]["AmazonEC2"]["savingsPlanVersionIndexUrl"])
        print(myJSON["offers"]["AmazonEC2"]["currentSavingsPlanIndexUrl"])


############################################
# MAIN CODE EXECUTION BEGIN
############################################
if __name__ == '__main__':
    #print('test')
    myObj = AWSPricing()
    myObj.getOfferIndexURL()
    #print("output: ",myObj.getSavingsPlanURL)