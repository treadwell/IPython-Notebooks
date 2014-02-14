# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Scheduled / Unscheduled Report (by page position)

# <codecell>

import re
import os

filename ='CDC0089 01-09-14.TXT'
path = '.'

files = os.listdir(os.getcwd())

class Facility(object):
    def __init__(self, date, loc):
        self.date = date
        self.loc = loc # location

    # properties:
    # location: Gahanna, Ashland, or Groveport
    # date
    # new: new_orders
    # sched: scheduled orders
    # unsched: unscheduled orders
    # ship: ship confirms
    # susp: suspended orders
    # old: old in process
    # future: future orders
    # hold: hold or problem orders

    self.labels = ['new', 'sched', 'unsched', 'ship',
                   'susp', 'old', 'future', 'hold']

    self.data = {}

    def process_line(self, label, line):
        assert label in labels
        if self.loc == "GAH":
            data = line[52:60]
        if self.loc == "ASH":
            data = line[90:96]
        if self.loc == "GRO":
            data = line[126:132]
        self.data[label] = data.replace(' ', '')

    def print_headers(self):
        return labels

    def print_line(self):
        return [self.data[label] for label in labels]

class OutputRow(object):
    """Holds three (or even four) Facility objects, for output"""
    def self.__init__(date, facilities):
        self.date = date
        assert facilities[0].__class__.__name__ == "Facility"
        assert set([f.loc for f in facilities])
               == set("GAH", "ASH", "GRO")
        self.facilities = facilities

    def print_facility_headers(self):
        return ["Gahanna"] + [""]*len(facilities[0].labels) +\
               ["Ashland"] + [""]*len(facilities[0].labels) +\
               ["Groveport"]

    def print_headers(self):
        return sum([f.labels for f in facilities])

    def print_row(self):
        return sum([f.print_line() for f in facilities])
         

output_rows = {} # map of dates to OutputRow objects
for f in filedir: # going over each file
    date = get_date(f)
    facilities = []
    for loc in ("GAH", "ASH", "GRO"):
        fac = Facility(date, loc)
        for line in f:
            # test that line has a label & get label
            label = "new"
            fac.process_line(line, label)
        facilities.append(fac)

    output_rows[date] = OutputRow(date, facilities)

### puts together a collection of OutputRow s

### when doing output:
csv_output = []

csv_output.append(output_rows.values[0].print_facility_headers)
csv_output.append(output_rows.values[0].print_headers)

for date in output_rows:
    csv_output.append(output_rows[date].print_row)
    

    

        
    
    # def line_processing(label,data):
    # # pass line in explicitly here
    # data["GAH_" + label] = 
    # data["ASH_" + label] = line[90:96].replace(' ','')
    # data["GRO_" + label] = line[126:132].replace(' ','')

print date, '\t', data['GAH_new'], '\t', data['GAH_sched'], '\t', data['GAH_unsched'], '\t','\t','\t', data['GAH_ship'], \
'\t', data['GAH_susp'], '\t', data['GAH_old'], '\t', data['GAH_future'], '\t', data['GAH_hold'], '\t', data['ASH_new'], \
'\t', data['ASH_sched'], '\t', data['ASH_unsched'], '\t', data['ASH_ship'], '\t', data['ASH_susp'], '\t', data['ASH_old'], \
'\t', data['ASH_future'], '\t', data['ASH_hold'], '\t', data['GRO_new'], '\t', data['GRO_sched'], '\t', data['GRO_unsched'], \
'\t', data['GRO_ship'], '\t', data['GRO_susp'], '\t', data['GRO_old'], '\t', data['GRO_future'], '\t', data['GRO_hold']
    




    
# initiliaze and comment your control variables here
page = 0 # page of the document that you're on

with open(path + filename) as f:
    data = {}
    # alternative: pull things directly by line number
    lines = list(f)
    # page 1
    line = lines[11]
    assert "TOTAL NEW ORDERS" in line
    line_processing(label, data)


    for line in f:
        if 'CDC0089-1' in line:
            if "1" in line[line.find('PAGE'):]:
                page = 1
                #print page
            if "2" in line[line.find('PAGE'):]:
                page = 2
                #print page
            if "3" in line[line.find('PAGE'):]:
                page = 3
                #print page
        if 'RUN DATE' in line and page == 1:
            for word in line.split():
                if '/' in word:
                    date = word
                    #print date
        if 'TOTAL NEW ORDERS' in line and page == 1:
            label = 'new'
            line_processing(label, data)
            #start_positions = [n for n in xrange(len(line)) if line.find('$', n) == n]
            #print "start_positions", start_positions
            #end_positions = [line.find(' ',posn) for posn in start_positions]
            #print "end_positions", end_positions
            #strings_test = [line[posn:line.find(' ',posn)] for posn in start_positions]

        if 'TOTAL SCHEDULED ORDERS' in line and page == 1:
            label = 'sched'
            line_processing(label, data)

        if 'TOTAL UNSCHEDULED ORDERS' in line and page == 1:
            label = 'unsched'
            line_processing(label, data)

        if 'TOTAL SHIPMENT CONFIRM' in line and page == 1:
            label = 'ship'
            line_processing(label, data)

        if 'SUSPENDED SHIPMENTS' in line and page == 1:
            label = 'susp'
            line_processing(label, data)

        if 'OLD INPROCESS (INP)' in line and page == 1:
            label = 'old'
            line_processing(label, data)

        if 'FUTURE DATED ' in line and page == 1:
            label = 'future'
            line_processing(label, data)

        if 'HOLDS / ERRORS' in line and page == 1:
            label = 'hold'
            line_processing(label, data)

            

print date, '\t', data['GAH_new'], '\t', data['GAH_sched'], '\t', data['GAH_unsched'], '\t','\t','\t', data['GAH_ship'], \
'\t', data['GAH_susp'], '\t', data['GAH_old'], '\t', data['GAH_future'], '\t', data['GAH_hold'], '\t', data['ASH_new'], \
'\t', data['ASH_sched'], '\t', data['ASH_unsched'], '\t', data['ASH_ship'], '\t', data['ASH_susp'], '\t', data['ASH_old'], \
'\t', data['ASH_future'], '\t', data['ASH_hold'], '\t', data['GRO_new'], '\t', data['GRO_sched'], '\t', data['GRO_unsched'], \
'\t', data['GRO_ship'], '\t', data['GRO_susp'], '\t', data['GRO_old'], '\t', data['GRO_future'], '\t', data['GRO_hold']




# how do I copy this to pasteboard automatically?
#output = date + '\t' + GAH_new + '\t' + GAH_sched
#print output

#cmd = 'echo %s | tr -d "\n" | pbcopy' % output
#os.system(output)

# <codecell>

import csv

save_filename = 'scheduled unscheduled.csv'

myCsvRow = [date, data['GAH_new'], data['GAH_sched'],  data['GAH_unsched'],'','', data['GAH_ship'], data['GAH_susp'], \
            data['GAH_old'],  data['GAH_future'],  data['GAH_hold'],  data['ASH_new'], \
            data['ASH_sched'], data['ASH_unsched'],  data['ASH_ship'],  data['ASH_susp'], data['ASH_old'], \
            data['ASH_future'], data['ASH_hold'],  data['GRO_new'],  data['GRO_sched'], data['GRO_unsched'], \
            data['GRO_ship'], data['GRO_susp'], data['GRO_old'], data['GRO_future'], data['GRO_hold']]

myfile = open(path + save_filename,'a')
writer = csv.writer(myfile)
writer.writerow(myCsvRow)
myfile.close()


# <headingcell level=1>

# Daily Sales Report (Excel file)

# <codecell>

import xlrd

filename ='112713.xls'
path = '/Users/kbrooks/Documents/MH/Projects/Metrics/CSOM/Daily Sales Report/'

files = os.listdir(path)

file_list = [file for file in files if '.xlsx' not in file]

file_list.sort()

#for file in file_list:
#    print file
    
filename=file_list[-1]
#print "file", filename

#print "Cell D30 is", sh.cell_value(rowx=29, colx=3)

#for rx in range(sh.nrows):
#    print sh.row(rx)
    # Refer to docs for more details.
    # Feedback on API is welcomed.
#Another quick start: This will show the first, second and last rows of each sheet in each file:

#    OS-prompt>python PYDIR/scripts/runxlrd.py 3rows *blah*.xls


book = xlrd.open_workbook(path + filename)

#print "The number of worksheets is", book.nsheets
#print "Worksheet name(s):", book.sheet_names()

sh = book.sheet_by_index(0)  # "sh" stands for "sheet"

#print sh.name, sh.nrows, sh.ncols

month_string = sh.cell(10,1).value

if month_string == 'November':
    month = '11'
elif month_string == 'December':
    month = '12'
elif month_string == 'January':
    month = '01'

date = month + "/" +str(int(sh.cell(10, 2).value)) + "/" +str(int(sh.cell(10, 4).value))
#print date

new_orders = sh.cell(32, 4).value
#print "New", new_orders
not_yet_processed = sh.cell(56, 4).value
#print "NYP", not_yet_processed
processed_not_shipped = sh.cell(44, 4).value
#print "pns", processed_not_shipped
pipeline = not_yet_processed + processed_not_shipped
#print "pipeline", pipeline
shipped_direct = sh.cell(22, 4).value
#print "shipped_direct", shipped_direct
shipped_depository = sh.cell(22, 5).value
#print "shipped_depository", shipped_depository

#print "Cell E16:", particular_cell_value

#for row in xrange(first_sheet.nrows):
#    for column in xrange(first_sheet.ncols):
#        print row, column, first_sheet.cell(row, column).value

print date,'\t',new_orders,'\t', not_yet_processed,'\t','\t',processed_not_shipped,'\t','\t',pipeline,'\t','\t',shipped_direct,'\t', shipped_depository

# <headingcell level=1>

# Scheduled / Unscheduled Report (by currency symbol)

# <codecell>

import os


filename ='CDC0089 01-01-14.TXT'
path = '/users/kbrooks/Documents/MH/Projects/Metrics/Distribution/Scheduled Unscheduled (CDC0089-1)/'

files = os.listdir(path)

for file in files:
    print file

def line_processing(line):
    new_list=[]
    for word in line.split():
        if '$' in word:
            new_list.append(word)
    return new_list

with open(path + filename) as f:
    pass_number = 0
    for line in f:
        if pass_number != 0: break
        if 'RUN DATE' in line:
            for word in line.split():
                if '/' in word:
                    date = word
                    print word
        if 'TOTAL NEW ORDERS' in line:
            new_orders = line_processing(line)
            print "New orders:", new_orders
        if 'TOTAL SCHEDULED ORDERS' in line:
            sched_orders = line_processing(line)
            print "Sched orders:", sched_orders
        if 'TOTAL UNSCHEDULED ORDERS' in line:
            unsched_orders = line_processing(line)
            print "Unsched orders:", unsched_orders
        if 'TOTAL SHIPMENT CONFIRM' in line:
            ship_confirms = line_processing(line)
            print "Ship confirms:", ship_confirms
        if 'SUSPENDED SHIPMENTS' in line:
            suspended = line_processing(line)
            print "Suspended:", suspended
        if 'OLD INPROCESS (INP)' in line:
            old_inprocess = line_processing(line)
            print "Old INP:", old_inprocess
        if 'FUTURE DATED ' in line:
            future = line_processing(line)
            print "Future:", future
        if 'HOLDS / ERRORS' in line:
            holds = line_processing(line)
            print "Holds:", holds
            pass_number = 1
            
if 3 in map(len, (new_orders, sched_orders, unsched_orders, ship_confirms,
                  suspended, old_inprocess, future, holds)):
    print "Blank line error"
    
print "-----------------"
print "Gahanna:", new_orders[0], '\t', sched_orders[0], '\t', unsched_orders[0], '\t','\t','\t', ship_confirms[0], '\t', suspended[0], '\t', old_inprocess[0], '\t', future[0], '\t', holds[0]
print "Ashland:", new_orders[1], '\t', sched_orders[1], '\t', unsched_orders[1], '\t', ship_confirms[1], '\t', suspended[1], '\t', old_inprocess[1], '\t', future[1], '\t', holds[1]
print "Groveport:", new_orders[2], '\t', sched_orders[2], '\t', unsched_orders[2], '\t', ship_confirms[2], '\t', suspended[2], '\t', old_inprocess[2], '\t', future[2], '\t', holds[2]
print "-----------------"
print date, '\t', new_orders[0], '\t', sched_orders[0], '\t', unsched_orders[0], '\t','\t','\t', ship_confirms[0], '\t', suspended[0], '\t', old_inprocess[0], '\t', future[0], '\t', holds[0],'\t', new_orders[1], '\t', sched_orders[1], '\t', unsched_orders[1], '\t', ship_confirms[1], '\t', suspended[1], '\t', old_inprocess[1], '\t', future[1], '\t', holds[1],'\t', new_orders[2], '\t', sched_orders[2], '\t', unsched_orders[2], '\t', ship_confirms[2], '\t', suspended[2], '\t', old_inprocess[2], '\t', future[2], '\t', holds[2]
        

# <codecell>


