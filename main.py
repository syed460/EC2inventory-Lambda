#!/bin/python3

import json, csv
import boto3
from pprint import pprint
from datetime import datetime
import subprocess
import os.path
  
#def lambda_handler(event, context):
print("-----------Script Starts-----------")
print("")
#-------------------filname function
Bucket_region = "eu-west-1"
Bucket_Name = "nonprodpatchinglogs"

#defining file name
def date_on_filename(filename, file_extension):  
	date = str(datetime.now().date())
	return filename + "-" + date + "." + file_extension

report_filename = date_on_filename("ec2_inventory", "csv")
print(f"output file name: {report_filename}")

#file path
filepath= "/tmp/" + report_filename
print(f"Output File Patch {filepath}")
print("")

#link the services
sts_cli=boto3.client(service_name='sts', region_name="us-east-1")
responce_1=sts_cli.get_caller_identity()
account_number=responce_1.get("Account")

#--------------Manually update the dic.keys() to header_list if mismatch

header_list=['region', 'OwnerId', 'IAMRole', 'image_id', 'Image_Name', 'InstanceId', 'InstanceType', 'KeyPair', 'LaunchTime', 'DetailedMonitoring', 'AZ', 'state', 'SubnetId', 'VpcId', 'DeviceNames', 'AttachedVolumeIds', 'EnaSupport', 'PrivateIpAddress', 'PublicIpAddress', 'RootDeviceType', 'SGId', 'SGName', 'SourceDestCheck']
print(header_list)
# to add 50 Tag headers
for v in range(1,50):
    header_list.append(f'Tag{v}')

#-----------collect all region list into Regions
print("collecting all the regions name")

ec2_cli = boto3.client(service_name='ec2', region_name="us-east-1")    
responce=ec2_cli.describe_regions()
#pprint(responce['Regions'])
Regions=[]
for each in responce['Regions']:
    #print(each['RegionName'])
    Regions.append(each['RegionName'])    
print(f"collected the {len(Regions)} regions")
print("")

#----------comment this one once testing done
#Regions=['us-east-1']
x=1 

#----------creating file with headder
print("Oppening the csv file to append each server details")
with open(filepath,'w') as csv_file:
#with open("outpu.csv",'w') as csv_file:
    Writer=csv.writer(csv_file)
    Writer.writerow(header_list)
    #Main_dic={}  

    #revert the changes here
    print("Now going through each regions to check ec2 details")
    print("")
    for region in Regions:
        #print(region)
        #print(type(region))
        ec2_cli=boto3.client(service_name='ec2', region_name=region)

        responce_instance=ec2_cli.describe_instances()
        #pprint(responce_instance)
        #print(" ")

        for key1, value1 in responce_instance.items():
            #print(key1)

            if key1 == "Reservations":
                #print(value1)

                for object_a in value1:
                    #pprint(object_a)
                    #print("------")

                    for key2, value2 in object_a.items():
                        #print(key2)
                        #print("---")

                        #dic = {}
                        #dic['region'] = region
                        #print(key2)
                          
                        if key2 == "Instances":
                            dic = {}
                             
                            dic['region'] = region
                            dic['OwnerId']=account_number
                            for object_b in value2:

                                #print(object_b)
                                for key3, value3 in object_b.items():
                                    if key3 == "State":
                                        state = value3['Name']
                                        dic['state']=state
                                        #print(dic)
                                    if key3 == "NetworkInterfaces":
                                        Network_interfaces_Count = str(len(value3))
                                        PrivateIpAddress=[]
                                        PublicIpAddress=[]
                                        

                                        for item in value3:
                                            try:
                                                PrivateIpAddress.append(item['PrivateIpAddress'])
                                                                                            
                                                #PublicIpAddress.append(item['Association']['PublicIp'])
                                            except Exception as e:
                                                PrivateIpAddress.append("None")
                                                #PublicIpAddress.append("None")
                                                #print("--------")
                                            try:
                                                                                                                                        
                                                PublicIpAddress.append(item['Association']['PublicIp'])
                                            except Exception as e:
                                                
                                                PublicIpAddress.append("None")
                                                #print("--------")    

                                        dic['PrivateIpAddress']=PrivateIpAddress
                                        dic['PublicIpAddress']=PublicIpAddress

                                    if key3 == "BlockDeviceMappings":
                                        DeviceNames=[]
                                        AttachedVolumeIds=[]
                                        for volume in value3:
                                            DeviceNames.append(volume['DeviceName'])
                                            AttachedVolumeIds.append(volume['Ebs']['VolumeId'])
                                        dic['DeviceNames']=DeviceNames
                                        dic['AttachedVolumeIds']=AttachedVolumeIds
                                    
                                    if key3 =="RootDeviceType":
                                        dic['RootDeviceType']=value3

                                    if key3 == "SourceDestCheck":
                                        if value3 == True:
                                            dic['SourceDestCheck']="Enabled"
                                        else:
                                            dic['SourceDestCheck']="Disabled"
                                    
                                    
                                    if key3 == "ImageId":
                                        image_id = value3
                                        dic['image_id']=image_id
                                        #print(image_id)
                                        #print(type(image_id))
                                        Image_Description = ec2_cli.describe_images(ImageIds=[image_id,])
                                        #pprint(Image_Description)
                                        if Image_Description['Images'] == []:
                                            #print("Image ID details not found")
                                            dic['Image_Name']= "Image Details Not Avaialble"

                                        else:
                                            #print("image details found")
                                            for image in Image_Description['Images']:
                                                #pprint(image)
                                                #print(image['Name'])
                                                #print("-------------")
                                                Image_Name = image['Description']
                                                dic['Image_Name']=Image_Name
                                                

                                    if key3 == "InstanceType":
                                        InstanceType=value3
                                        dic['InstanceType']=InstanceType
                                        #print(InstanceType)
                                        #print(type(InstanceType))
                                    if key3 == "VpcId":
                                        VpcId=value3
                                        dic['VpcId']=VpcId
                                        #print(VpcId)
                                        #print(type(VpcId))
                                    if key3 == "InstanceId":
                                        InstanceId=value3
                                        dic['InstanceId']=InstanceId
                                        #print(InstanceId)
                                        #print(type(InstanceId))
                                    if key3 == "LaunchTime":
                                        launch_time=str(value3)
                                        LaunchTime=datetime.strptime(launch_time, "%Y-%m-%d %H:%M:%S+00:00")
                                        
                                        #print(type(value3))
                                        LaunchTime_1=LaunchTime.strftime("%m/%d/%Y, %H:%M:%S")
                                        dic['LaunchTime']=LaunchTime_1
                                        #print(LaunchTime_1)
                                        #print(type(LaunchTime_1))
                                        #print(LaunchTime)
                                    if key3 == "SubnetId":
                                        SubnetId=value3
                                        dic['SubnetId']=SubnetId
                                        #print(SubnetId)
                                        #print(type(SubnetId))
                                    if key3 == "Platform":
                                        Platform=value3
                                        dic['Platform']=Platform
                                        #print(Platform)
                                        #print(type(Platform))
                                    if key3 == "KeyName":
                                        KeyPair=value3
                                        dic['KeyPair']=KeyPair
                                        #print(KeyPair)
                                        #print(type(KeyPair))
                                    if key3 == "Monitoring":
                                        DetailedMonitoring=value3['State']
                                        dic['DetailedMonitoring']=DetailedMonitoring
                                        #print(DetailedMonitoring)
                                        #print(type(DetailedMonitoring))
                                        #print(DetailedMonitoring)
                                    if key3 == "Placement":
                                        AZ=value3['AvailabilityZone']
                                        dic['AZ']=AZ
                                        #print(Zone)
                                        #print(type(Zone))
                                    if key3 == "EnaSupport":
                                        EnaSupport=str(value3)
                                        dic['EnaSupport']=EnaSupport
                                        #print(type(EnaSupport))
                                    
                                    if key3 == "IamInstanceProfile":
                                        IamRole = value3['Arn']
                                        dic['IAMRole']=IamRole
                                        #print(IamRole)
                                        #print(type(IamRole))
                                    
                                    if dic.get('IAMRole') == None:
                                        dic['IAMRole']="IAMRole Not Available"

                                    if key3 == "SecurityGroups":
                                        SGId=[]
                                        SGName=[]   
                                        #print(type(SGName))
                                        for each in value3:
                                            SGName.append(each['GroupName'])
                                            SGId.append(each['GroupId'])
                                        dic["SGId"]=SGId
                                        dic['SGName']=SGName
                                        #print(f"SG name {SGId}")
                                        #print(type(SGId))
                                        #print(f"SG name {SGName}")
                                        #print(type(SGName))
                                    b=1
                                    if key3 == "Tags":
                                        #print(value3)
                                        #print("---------------")
                                        for each in value3:
                                            print(list(each.values()))
                                            dic[f'Tag{b}']=list(each.values())
                                            b+=1

                                    

                            #Add account id
                            
                            #Check IAMRole Role
                            
                                #print("IAMRole not attached")                                
                            #print(f"filnal line {x} \n--------")
                            #print(len(dic.keys()))

                            #Finally          
                            print("-----")                 
                            print(dic.keys()) 
                            print("-----")                 
                            #print(dic.values())
                            
                            Writer.writerow(dic.values())
                            print(f"Added this {x} instance dtails to {report_filename}")
                            print("------")
                            print('')
                            x=x+1



#to check the what are the files exist under folder
lscommand = subprocess.run("ls /tmp/ec2_inventory*", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(lscommand.stdout.decode('utf-8'))

#transfer the file to s3
s3_cli=boto3.client(service_name='s3', region_name=Bucket_region)
s3_cli.upload_file(filepath, Bucket_Name, report_filename)

#remove the file from container
removefile=subprocess.run("rm -rfv /tmp/ec2_inventory*", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(removefile.stdout.decode('utf-8'))
print(" ")
print("----------Script Ends-----------")