# aws_prices
For purposes of fetching AWS pricing related to 3Y All Upfront Compute Savings Plan

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
This is for writing to Excel workbook.  
To install use  
```
pip3 install xlsxwriter
```


### Reference links 

[AWS Bulk API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/using-ppslong.html)  
[Savings plan offer file](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/sp-offer-file.html)
