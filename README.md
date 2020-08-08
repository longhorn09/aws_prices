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
Python script will create an Excel file with `.xlsx` file extension with the Savings Plan quotes

### Dependencies
Script relies up on `xlsxwriter`  
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

### Reference links 

[AWS Bulk API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-ppslong.html)  
[Savings plan offer file](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/sp-offer-file.html)
