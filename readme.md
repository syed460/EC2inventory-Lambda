# EC2 Inverntory details

It collects the inventory details of all the Ec2 instances of All the regions in a account into CSV file and pushes the file to S3 bucket.

How i have done:
    > used boto3 to create a dictionary with all the details i want
    > created csv file header with the dictionary key
    > created csv file rows with the dictionary values
    