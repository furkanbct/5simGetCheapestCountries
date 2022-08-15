from requests import get
from collections import OrderedDict
from xlwt import Workbook
from sys import path
from os.path import join

countries_data = get("https://5sim.net/v1/guest/countries").json()

countries = {}
for key, values in countries_data.items():
    countries[key] = {"Virtuals": [value for value in values.keys() if value.startswith("virtual")]}

services = {}
service_ask = input("Enter service: ").lower()
print("Please Wait ...")

for country, value in countries.items():
    virtualsPrices = {}
    sortedVirtualPrices = {}
    for virtual in value["Virtuals"]:
        products_data = get(f"https://5sim.net/v1/guest/products/{country}/{virtual}").json()
        if service_ask in products_data.keys():
            virtualsPrices[virtual] = {"Price": products_data[service_ask]["Price"], "Stock": products_data[service_ask]["Qty"]}

    sortedVirtualPrices = OrderedDict(sorted(virtualsPrices.items(),key=lambda kv: kv[1]["Price"],reverse=False))
    for virtual in sortedVirtualPrices:
        if sortedVirtualPrices[virtual]["Stock"] != 0:
            services[country] = {"price": sortedVirtualPrices[virtual]["Price"], "stok": sortedVirtualPrices[virtual]["Stock"], "virtual": virtual}
            break

sortedServices = OrderedDict(sorted(services.items(),key=lambda kv: kv[1]["price"],reverse=False))
for service in sortedServices:
    print(service, f"Price :{sortedServices[service]['price']}", f"Stock :{sortedServices[service]['stok']}", f"Virtual :{sortedServices[service]['virtual']}")

excel_ask = input("Do you want export to Excel file ? (Y/N) :").lower()
if excel_ask == "y":
    wb = Workbook()
    ws = wb.add_sheet("Sheet 1")
    for row, service in enumerate(sortedServices):
        ws.write(row,0,service)
        ws.write(row,1,sortedServices[service]["price"])
        ws.write(row,2,sortedServices[service]["stok"])
        ws.write(row,3,sortedServices[service]["virtual"])
    print(join(path[0], "5sim.xls"))
    wb.save(join(path[0], "5sim.xls"))
    print("Exported to 5sim.xls")
input("Press Enter to exit")