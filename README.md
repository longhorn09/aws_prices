# aws_prices
Fetching AWS price quotes related to 3Y All Upfront Compute Savings Plan with output in an Excel file.

### Installation
```
git clone git@github.com:longhorn09/aws_prices.git  
pip3 install xlsxwriter
```

### Running
```   
python3 index.py
```

### Output
Python script will create an Excel file with Savings Plan quotes and filename of 
```
sp_prices.xlsx
```
in same folder where python script is run. Can easily filter or use `vlookup()` or any other excel lookup technique such as `xlookup()` or `index/match`

![Excel screenshot](https://user-images.githubusercontent.com/11417589/89704400-28320d00-d919-11ea-87a8-5fd1e06f4b66.png)

### Dependencies
Script relies upon `xlsxwriter`  
This is for writing to Excel workbook. To install use `pip3` as shown below
```
pip3 install xlsxwriter
```
### Performance tweaks
Each regional savings plan URL ranges from 40~70 MB.  
The list of EC2 offers is roughly 1.3GB. Even over gigabit fiber connections, it can take a while to download/read.  
Because of this, if repeatedly running this script, save the 1.3GB JSON file locally, and toggle within the `getSKUListLocal` function and tweak the file name accordingly.

```
doLocal = True  # toggle

if (doLocal):
    # this is a 1.3 GB file - may take time
    with open('index_aws_ec2.json') as json_file: 
        myJSON = json.load(json_file)   
```


### JSON reference snippets
3Y Compute Savings Plan All Upfront has product sku of `RQRC4CUNT9HUG9WC`  
```
{
    "sku" : "RQRC4CUNT9HUG9WC",
    "productFamily" : "ComputeSavingsPlans",
    "serviceCode" : "ComputeSavingsPlans",
    "usageType" : "ComputeSP:3yrAllUpfront",
    "operation" : "",
    "attributes" : {
      "purchaseOption" : "All Upfront",
      "granularity" : "hourly",
      "purchaseTerm" : "3yr",
      "locationType" : "AWS Region",
      "location" : "Any"
    }
  }
```

### Reference links 

[AWS Bulk API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-ppslong.html)  
[Savings plan offer file](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/sp-offer-file.html)  
[JSON Editor online](https://jsoneditoronline.org/#left=url.https%3A%2F%2Fpricing.us-east-1.amazonaws.com%2FsavingsPlan%2Fv1.0%2Faws%2FAWSComputeSavingsPlan%2F20200806153551%2Fus-east-2%2Findex.json)  
[AmazonEC2.currentVersionUrl (1.3GB)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json)  
[AmazonEC2.currentRegionIndexUrl ](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/region_index.json)  
[AmazonEC2.currentSavingsPlanIndexUrl ](https://pricing.us-east-1.amazonaws.com/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/region_index.json)  
  
