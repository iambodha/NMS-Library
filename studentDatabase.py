import csv

#Append(Add) a
#Read r
#Write w+

new_data = ["Elias", 2915, "7C", "2915@nms-berlin.de"]

with open("student.csv", mode="a") as file:
    writer = csv.writer(file)
    writer.writerow(new_data)
