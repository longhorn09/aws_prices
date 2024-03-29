# aws_prices
Fetching AWS price quotes related to 3Y All Upfront Compute Savings Plan with output in an Excel file.  
Also pulls in `1yrNoUpfront` Compute Savings plan as of 12/03/2020.

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


### Issues
If the Excel file isn't created upon running the script, the likely cause is due to executing Python within WSL (Ubuntu) environment. I think there may be a hidden permissions issue that recently surfaced that oddly doesn't trigger any error messages nor warnings.

The workaround is to install Python to Windows natively and run python from the DOS prompt command line. At which point the `.xlsx` output file will be created. 

### Dependencies
Script relies upon `xlsxwriter`  
This is for writing to Excel workbook. To install use `pip3` as shown below
```
pip3 install xlsxwriter
```
### Performance tweaks
Each regional savings plan URL ranges from 40 MB to 0.1GB.  
The list of EC2 offers is roughly 1.3GB. Even over gigabit fiber connections, it can take a while to download/read.  
Because of this, if repeatedly running this script, save the 1.3GB JSON file locally, and toggle within the `getSKUListLocal` function and tweak the file name accordingly.

These toggles are around line 142 and line 224 of the code base.
`doLocal = True` or `doLocal = False`

```
doLocal = True  # toggle

if (doLocal):
    # this is a 1.3 GB file - may take time
    with open('index_aws_ec2.json') as json_file: 
        myJSON = json.load(json_file)   
```


### JSON reference snippets
When reading from [Offer index file](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json) for `AmazonEC2`, look to `currentVersionUrl` and `currentSavingsPlanIndexUrl`

```
    "AmazonEC2" : {
      "offerCode" : "AmazonEC2",
      "versionIndexUrl" : "/offers/v1.0/aws/AmazonEC2/index.json",
      "currentVersionUrl" : "/offers/v1.0/aws/AmazonEC2/current/index.json",
      "currentRegionIndexUrl" : "/offers/v1.0/aws/AmazonEC2/current/region_index.json",
      "savingsPlanVersionIndexUrl" : "/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/index.json",
      "currentSavingsPlanIndexUrl" : "/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/region_index.json"
    },
```

When looking up respective savings plan Url in [region_index.json](https://pricing.us-east-1.amazonaws.com/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/current/region_index.json), look to `versionUrl`

```
  "regions" : [ {
    "regionCode" : "ap-south-1",
    "versionUrl" : "/savingsPlan/v1.0/aws/AWSComputeSavingsPlan/20200806153551/ap-south-1/index.json"
  }, {
```    

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

Once the product sku is found, then combine that with the other sku to match by `rateCode` so you can find the correct corresponding `discountedRate`
```
, {
    "discountedSku" : "TBV6C3VKSXKFHHSC",
    "discountedUsageType" : "USE2-BoxUsage:t3a.xlarge",
    "discountedOperation" : "RunInstances",
    "discountedServiceCode" : "AmazonEC2",
    "rateCode" : "RQRC4CUNT9HUG9WC.TBV6C3VKSXKFHHSC",
    "unit" : "Hrs",
    "discountedRate" : {
      "price" : "0.0679",
      "currency" : "USD"
    }
```


### Reference links 

[AWS Bulk API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-ppslong.html)  
[Savings plan offer file](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/sp-offer-file.html)  
[JSON Editor online](https://jsoneditoronline.org/#left=url.https%3A%2F%2Fpricing.us-east-1.amazonaws.com%2FsavingsPlan%2Fv1.0%2Faws%2FAWSComputeSavingsPlan%2F20200806153551%2Fus-east-2%2Findex.json)  
[AmazonEC2.currentVersionUrl (1.3GB)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json)  

  
