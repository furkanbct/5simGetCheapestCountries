import requests
from collections import OrderedDict
import xlwt
import sys
import os

session = requests.session()

get = session.get("https://5sim.net/v1/guest/countries")

countries = {}
datas = get.json()
for x in datas:
    virtualsList = []
    for i in range(100):
        try:
            datas[x]["virtual"+str(i)]
            virtualsList.append("virtual"+str(i))
        except:
            None
    countries.update({x:{"Virtuals":virtualsList}})
services = {}
service = input("Enter service: ")
print("Please Wait ...")
for i in countries:
    virtualsPrices = {}
    sortedVirtualPrices = {}
    for virtual in countries[i]["Virtuals"]:
        get = session.get("https://5sim.net/v1/guest/products/"+i+"/"+virtual)
        try:
            a = get.json()[str(service)]
            virtualsPrices.update({virtual:{"Price":a["Price"],"Stock":a["Qty"]}})
        except:
            pass
    sortedVirtualPrices = OrderedDict(sorted(virtualsPrices.items(),key=lambda kv: kv[1]["Price"],reverse=False))
    for f in sortedVirtualPrices:
        if sortedVirtualPrices[f]["Stock"] != 0:
            services.update({i:{"price":sortedVirtualPrices[f]["Price"],"stok":sortedVirtualPrices[f]["Stock"],"virtual":f}})
            break
        
sortedServices = OrderedDict(sorted(services.items(),key=lambda kv: kv[1]["price"],reverse=False))
for b in sortedServices:
    print(b,"Price :{0}".format(sortedServices[b]["price"]),"Stock :{0}".format(sortedServices[b]["stok"]),"Virtual :{0}".format(sortedServices[b]["virtual"]))

k = input("Do you want export to Excel file ? (Y/N) :")
if(k == "Y" or k == "y"):
    wb = xlwt.Workbook()
    ws = wb.add_sheet("Sheet 1")
    row = 0
    for i in sortedServices:
        ws.write(row,0,i)
        ws.write(row,1,sortedServices[i]["price"])
        ws.write(row,2,sortedServices[i]["stok"])
        ws.write(row,3,sortedServices[i]["virtual"])
        row += 1
    print(os.path.join(sys.path[0], "5sim.xls"))
    wb.save(os.path.join(sys.path[0], "5sim.xls"))
    print("Exported to 5sim.xls")
input("Press Enter to exit")