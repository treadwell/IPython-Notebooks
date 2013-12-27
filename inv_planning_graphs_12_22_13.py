# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

#from ggplot import *
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr

# <codecell>

# set path to working directory

path = '/Users/kbrooks/Documents/TMG/Companies/Ingram/Inventory/Inventory Charts/'

# set costs

cost = {'perOrder': 80.0, 'WACC': 0.12, 'POD_vmc': 5.0, 'fmc': 1000, 
        'vmc': 2.0, 'lost_margin': 20.00, 'allow_POD':True}

# set forecast parameters

starting_monthly_demand = 1000
number_months = 36
trendPerMonth = -0.05
seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]

# set returns parameters

returns_rate = 0.2
lag = 3

# set other parameters

inv_0 = 0  # starting inventory...not tested
replen_lead_time = 2

# <headingcell level=1>

# 1. Start with a forecast of demand

# <codecell>

# Start with a forecast of demand

#%pylab inline
month = [i+1 for i in xrange(number_months)]

level = [starting_monthly_demand] * number_months

trend = [int(x * (1+trendPerMonth)**i) for i, x in enumerate(level)]

forecast = [int(x*seasonCoeffs[i % 12]) for i, x in enumerate(trend)]

#print "forecast:", forecast

### determine which plots turn up
plots_to_show = [10]
def show_if(n):
    if n in plots_to_show:
        plt.show(n)
    plt.clf()

# plot forecast
plt.plot(month,forecast, linewidth=2.0, label='demand forecast')
plt.ylabel('Units')
plt.xlabel('Month')
plt.title('1. Start with a forecast of demand...', y=1.05, weight = "bold")
plt.legend()
show_if(1)

# <headingcell level=1>

# 2. ...and a forecast of returns

# <codecell>

# returns forecast

returns = [0]*number_months

for i,x in enumerate(forecast):
    if i < lag:
        returns[i] = 0
    else:
        returns[i] = int(returns_rate*forecast[i-lag])
    #print i
    #print "forecast:", forecast[i]
    #print "returns:", returns[i]

#print "forecast:", forecast
#print "returns:", returns

plt.plot(month,forecast, linewidth=2.0, label='demand forecast')
plt.plot(month,returns, linewidth=2.0, label='returns forecast')
plt.ylabel('Units')
plt.xlabel('Month')
plt.title('2. ...and a forecast of returns.', y=1.05, weight = "bold")
plt.legend()
show_if(2)

# <headingcell level=1>

# 3. use planned purchases, demand, and returns to calculate inventory position...

# <codecell>

# revised logic with ROP

reorder_point = [0] * len(month)

def calc_POD_breakeven(cost):
    # note that this should really incorporate WACC
    return cost['fmc']/(cost['POD_vmc']-cost['vmc'])

POD_breakeven = calc_POD_breakeven(cost)

def determine_plan(forecast, returns, reorder_point, 
                cost, inv_0 = 0):
    starting_inventory = []
    ending_inventory = []
    average_inventory = []
    POD_orders = [0]*len(forecast)
    orders=[0]*len(forecast)

    for i, fcst in enumerate(forecast):
        # calculate starting inventory
        if i == 0:
            starting_inventory.append(inv_0)
        else:
            starting_inventory.append(ending_inventory[i-1])
        # calculate trial ending inventory
        trial_ending_inventory = starting_inventory[i] - fcst + returns[i]
        # if trial ending inventory < ROP, place order
        if trial_ending_inventory < reorder_point[i]:
            # determine order quantity
            # orders = current shortfall + order quantity
            n=9
            orders[i] = sum(forecast[i:i+n])-sum(returns[i:i+n])
            # order POD if the size of the order is too small
            # POD order quantity will be just what is needed in the current month
            if orders[i] < calc_POD_breakeven(cost) and cost['allow_POD'] == True:
                POD_orders[i] = max(forecast[i]-starting_inventory[i]-returns[i],0)
                orders[i] = 0
        else:
            orders[i] = 0
        # calculate ending inventory from inventory balance equation
        ending_inventory.append(starting_inventory[i] - forecast[i] + returns[i]
                                    + orders[i] + POD_orders[i])
        #print i
        #print "orders:", orders[i]
        #print "POD_orders:", POD_orders[i]
        #print "start_inv:", starting_inventory[i]
        #print "end_inv:", ending_inventory[i]

        # calculate average inventory in order to calculate period carrying cost
        average_inventory.append((starting_inventory[i]+ending_inventory[i])/2)

    return orders, POD_orders, starting_inventory, ending_inventory, average_inventory

orders, POD_orders, start_inv, end_inv, avg_inv = determine_plan(forecast, returns, [0]* number_months, cost)

#print "orders:", orders
#print "POD_orders:", POD_orders
#print "start_inv:", start_inv
#print "end_inv:", end_inv
#print "avg_inv:", avg_inv

plt.plot(month,end_inv, linewidth=2.0, color = "g",label='ending inventory')
d = np.array([0]*len(forecast))
plt.fill_between(month, d, end_inv, where=end_inv>=d, interpolate=True, facecolor='green')
plt.ylabel('Units')
plt.xlabel('Month')
plt.title('3. Use planned purchases, demand, \nand returns to calculate inventory position...', y=1.05, weight = "bold")
plt.legend()

show_if(3)

# <headingcell level=1>

# 4. ...yielding a lifetime expected cost.

# <codecell>

# Fixed manufacturing cost - fmc
# per order cost - perOrder
# variable manufacturing cost - vmc
# variable manufacturing cost of POD - POD_vmc
# WACC for pricing inventory carrying cost - WACC


def calc_costs(orders, POD_orders, avg_inv, cost):
    FMC = [cost['fmc'] + cost['perOrder'] if round(order) else 0 for order in orders]
    VMC = [cost['vmc'] * order for order in orders]
    POD_VMC = [cost['POD_vmc'] * POD_order for POD_order in POD_orders]
    umc = (sum(FMC)+sum(VMC)+sum(POD_VMC)) / (sum(orders)+sum(POD_orders)) # approximation - should be a list
    carry_stg_cost = [float(cost['WACC']) / 12 * month_avg * umc for month_avg in avg_inv] 

    return FMC, VMC, POD_VMC, umc, carry_stg_cost

FMC, VMC, POD_VMC, umc, carry_stg_cost = calc_costs(orders, POD_orders, avg_inv, cost)

# -----------------------------
#   Stockout cost:  Work this out
# -----------------------------

print "Gaussian CDF/surplus:" #(inventory, mean, std dev)
inventory, mean_demand, std_dev_demand = 11000, 1000, 100
my_books = stats.norm(loc = mean_demand, scale = std_dev_demand)
print my_books.cdf(inventory) ### un_normalize the CDF
# print "Gaussian survival function:"
# print stats.norm.sf(1.96, loc=0, scale=1)  # s/b 1-cdf
# print "reverse survival:"
# print stats.norm.isf(0.0249978951482, loc = 0, scale=1)

#point to integrate from: inventory
# expected loss: SF(inventory, loc=mean, scale = std_dev) * scale
# expected surplus: CDF(inventory, loc = mean, scale = std_dev) * scale

raise


#------------------------------
print "Total FMC:", sum(FMC)
print "Total VMC:", sum(VMC)
print "Total POD VMC:", sum(POD_VMC)
print "umc:", umc
print "Total carrying / storage cost:", sum(carry_stg_cost)


# plot results
N = 4
FMC_plot   = (sum(FMC), sum(FMC), sum(FMC), sum(FMC))
VMC_plot = (sum(VMC), sum(VMC), sum(VMC), sum(VMC))
PODVMC_plot     = (sum(POD_VMC), sum(POD_VMC), sum(POD_VMC), sum(POD_VMC))
carry_storage_plot   = (sum(carry_stg_cost), sum(carry_stg_cost), sum(carry_stg_cost), sum(carry_stg_cost))
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, FMC_plot,   width, color='r')
p2 = plt.bar(ind, VMC_plot, width, color='g', bottom=FMC_plot)
p3 = plt.bar(ind, PODVMC_plot, width, color='b', bottom=VMC_plot)
p4 = plt.bar(ind, carry_storage_plot, width, color='k', bottom=PODVMC_plot)

plt.ylabel('Cost ($)')

plt.title('4. ...yielding a lifetime expected cost.', y=1.05, weight = "bold")
plt.xticks(ind+width/2., ('Plan', 'Act w Lost Sales', 'Act w SS', 'Act w POD') )
#plt.yticks(np.arange(0,81,10))
plt.legend( (p1[0], p2[0],p3[0],p4[0]), ('FMC', 'VMC', 'POD VMC', 'Carry/Storage') )
show_if(4)

# <headingcell level=1>

# 5. But forecasts are wrong...

# <codecell>

initial_cv = 0.15
per_period_cv = 0.015
sd_forecast = [(initial_cv + i*per_period_cv) * monthly_forecast for i, monthly_forecast in enumerate(forecast)]

##############################
np.random.seed(5)
############################## 3, 4, 

demand = [max(round(np.random.normal(fcst, sd)),0) for fcst, sd in zip(forecast, sd_forecast)]
lower_CI = [fcst - 1.96 * sd for fcst, sd in zip(forecast, sd_forecast)]
upper_CI = [fcst + 1.96 * sd for fcst, sd in zip(forecast, sd_forecast)]


plt.plot(month,forecast, linewidth=2.0, label='demand forecast')
plt.plot(month,demand, linewidth=2.0, label='actual demand')
plt.plot(month,upper_CI, linewidth=0.5, label='95% CI', color="blue")
plt.plot(month,lower_CI, linewidth=0.5, color="blue")
plt.ylabel('Units')
plt.xlabel('Month')
plt.title('5. But forecasts are wrong...', y=1.05, weight = "bold")
plt.legend()

show_if(5)

# <headingcell level=1>

# 6. ...leading to stockouts with lost sales and expediting...

# <codecell>

def inv_from_demand(demand, orders, POD_orders, returns):

    start_inv_act = []
    start_inv_posn_act = []
    end_inv_act = []
    end_inv_posn_act = []
    avg_inv_act = []

    for i, order in enumerate(orders):
        # calculate starting inventory
        if i == 0:
            start_inv_act.append(max(0,inv_0))  # eventually replace this with an optional input
            start_inv_posn_act.append(0)
        else:
            start_inv_act.append(end_inv_act[i-1])
            start_inv_posn_act.append(end_inv_posn_act[i-1])
        
        # calculate ending inventory from inventory balance equation
        end_inv_act.append(max(0,start_inv_act[i] - demand[i] + orders[i] + 
                               POD_orders[i] + returns[i]))
        end_inv_posn_act.append(start_inv_posn_act[i] - demand[i] + orders[i] + 
                                POD_orders[i] + returns[i])

        # calculate average inventory in order to calculate period carrying cost
        avg_inv_act.append((start_inv_act[i]+end_inv_act[i])/2)
    
    return end_inv_posn_act, avg_inv_act

#month=[i+1 for i in xrange(12)]
#demand = [1000]*12
#forecast = [1000]*12
#returns = [0]*12
#orders = [6000,0,0,0,0,0]*2
#POD_orders = [0]*12


end_inv_posn_act, avg_inv_act = inv_from_demand(demand, orders, POD_orders, returns)

#print month
#print "forecast:", forecast
#print "demand:", demand
#print "returns:", returns
#print "orders:", orders
#print "POD_orders:", POD_orders
#print "start_inv:", start_inv
#print "end_inv:", end_inv
#print "avg_inv:", avg_inv
#print end_inv_posn_act

#print inventory_plot
plt.plot(month,end_inv_posn_act, linewidth=2.0, 
         label='end inventory position', color='green')
d = np.array([0]*len(forecast))
plt.fill_between(month, d, end_inv_posn_act, where=end_inv_posn_act<=d, interpolate=True, facecolor='red')
plt.fill_between(month, d, end_inv_posn_act, where=end_inv_posn_act>=d, interpolate=True, facecolor='green')
plt.ylabel('Units')
plt.xlabel('Month')
plt.title('6. ...leading to stockouts with lost sales and expediting...', y=1.05, weight = "bold")
plt.legend()
show_if(6)

# <headingcell level=1>

# 7. ...and additional costs.

# <codecell>

# edit these
FMC_act = [cost['fmc'] + cost['perOrder'] if round(order) else 0 for order in orders]
VMC_act = [cost['vmc'] * order for order in orders]
POC_VMC_act = [cost['POD_vmc'] * POD_order for POD_order in POD_orders]
umc_act = (sum(FMC)+sum(VMC)+sum(POD_VMC)) / (sum(orders)+sum(POD_orders)) # approximation - should be a list
carry_stg_cost_act = [float(cost['WACC']) / 12 * month_avg * umc for month_avg in avg_inv_act] 
lost_sales_act = [-posn * cost['lost_margin'] if posn < 0 else 0 for posn in end_inv_posn_act]

print "Total actual FMC:", sum(FMC)
print "Total actual VMC:", sum(VMC)
print "Total actual POD VMC:", sum(POD_VMC)
print "actual umc:", umc
print "Total actual carrying / storage cost:", sum(carry_stg_cost)
print "Total actual lost sales:", sum(lost_sales_act)


N = 4
FMC_plot   = (sum(FMC), sum(FMC), sum(FMC), sum(FMC))
VMC_plot = (sum(VMC), sum(VMC), sum(VMC), sum(VMC))
PODVMC_plot     = (sum(POD_VMC), sum(POD_VMC), sum(POD_VMC), sum(POD_VMC))
carry_storage_plot   = (sum(carry_stg_cost), sum(carry_stg_cost), 
                        sum(carry_stg_cost), sum(carry_stg_cost))
lost_sales_plot = (0, sum(lost_sales_act), 0, 0)
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

p1 = plt.bar(ind, FMC_plot,   width, color='r')
p2 = plt.bar(ind, VMC_plot, width, color='g', bottom=FMC_plot)
p3 = plt.bar(ind, PODVMC_plot, width, color='b', bottom=VMC_plot)
p4 = plt.bar(ind, carry_storage_plot, width, color='k', 
             bottom=PODVMC_plot)
p5 = plt.bar(ind, lost_sales_plot, width, color='y', 
             bottom=carry_storage_plot)

plt.ylabel('Cost ($)')

plt.title('7. ...and additional costs.', y=1.05, weight = "bold")
plt.xticks(ind+width/2., ('Plan', 'Act w Lost Sales', 'Act w SS', 'Act w POD') )
#plt.yticks(np.arange(0,81,10))
plt.legend( (p1[0], p2[0],p3[0],p4[0], p5[0]), ('FMC', 'VMC', 'POD VMC', 'Carry/Storage', 'Lost Sales') )
show_if(7)

# <markdowncell>

# *	Customers may get stock from elsewhere
# *	Customers may cancel the order and order again
# *	Customers may backorder until you're back in stock
# *	The cost of the backorder can also vary significantly
#     *	proportional to lifetime value if it's an adoption
#     *	Loss of marginal cost early in the life
#     *	etc.
# *	most estimates put the loss at around 7% of the units
# 
# Note there are many things that will keep you from actually having to incur this cost:

# <headingcell level=1>

# 8. The usual approach to avoid lost sales is to carry safety stock

# <codecell>

# develop plan with ROPs loaded

reorder_point = [int((replen_lead_time)**0.5 * 1.96 * sd) for sd in sd_forecast]
print reorder_point


orders_ss, POD_orders_ss, start_inv_ss, end_inv_ss, avg_inv_ss = determine_plan(forecast, returns, reorder_point, cost)

FMC_ss, VMC_ss, POD_VMC_ss, umc_ss, carry_stg_cost_ss = calc_costs(orders_ss, POD_orders_ss, avg_inv_ss, cost)

plt.plot(month,end_inv, linewidth=2.0, label='end inventory position', 
         color ='green')
d = np.array([0]*number_months)
plt.fill_between(month, d, end_inv_ss, where=end_inv<=d, 
                 interpolate=True, facecolor='red')
plt.fill_between(month, d, end_inv_ss, where=end_inv>=d, 
                 interpolate=True, facecolor='green')
plt.ylabel('Units')
plt.xlabel('Month')
plt.title('8. The usual approach to avoid lost sales\nis to carry safety stock.', y=1.05, weight = "bold")
plt.legend()
show_if(8)

# <headingcell level=1>

# 9. Another is to use POD.

# <codecell>

	
#	 - it looks like lost sales, but is cheaper
#  put the lost sales numbers into the POD vector and recalc positions and costs
# Use the lost sales line chart with a note about the cost of a lost sale
#  revalued_lost_sales = [0]*len(forecast)
lost_sales_as_POD = [-posn * cost['POD_vmc'] if posn < 0 else 0 for posn in end_inv_posn_act]

print "Total actual FMC:", sum(FMC)
print "Total actual VMC:", sum(VMC)
print "Total actual POD VMC:", sum(POD_VMC)
print "actual umc:", umc
print "Total actual carrying / storage cost:", sum(carry_stg_cost)
print "Total actual lost sales (as POD):", sum(lost_sales_as_POD)

# this should be the same as the lost sale area chart

plt.plot(month,end_inv_posn_act, linewidth=2.0, 
         label='end inventory position', color='green')
d = np.array([0]*len(forecast))
plt.fill_between(month, d, end_inv_posn_act, where=end_inv_posn_act<=d, interpolate=True, facecolor='blue')
plt.fill_between(month, d, end_inv_posn_act, where=end_inv_posn_act>=d, interpolate=True, facecolor='green')
plt.ylabel('Units')
plt.xlabel('Month')
plt.title('9. Another is to use POD.', y=1.05, weight = "bold")
plt.legend()
show_if(9)

# <headingcell level=1>

# 10. POD is best.

# <rawcell>

# Show stacked bars of the three alternatives or three panels

# <headingcell level=2>

# Lost sales alternative

# <codecell>

print "Total actual FMC:", sum(FMC)
print "Total actual VMC:", sum(VMC)
print "Total actual POD VMC:", sum(POD_VMC)
print "actual umc:", umc
print "Total actual carrying / storage cost:", sum(carry_stg_cost)
print "Total actual lost sales:", sum(lost_sales_act)
print "Grand total with lost sales:", sum(FMC)+sum(VMC)+sum(POD_VMC)+sum(carry_stg_cost)+sum(lost_sales_act)

# <headingcell level=2>

# Safety stock alternative

# <codecell>

# change to capture new FMC, VMC etc w POD
print "Total actual FMC:", sum(FMC_ss)
print "Total actual VMC:", sum(VMC_ss)
print "Total actual POD VMC:", sum(POD_VMC_ss)
print "actual umc:", umc
print "Total actual carrying / storage cost:", sum(carry_stg_cost_ss)
print "Grand total with safety stock:", sum(FMC_ss)+sum(VMC_ss)+sum(POD_VMC_ss)+sum(carry_stg_cost_ss)

# extra costs come from printing more

# <headingcell level=2>

# POD alternative

# <codecell>

print "Total actual FMC:", sum(FMC)
print "Total actual VMC:", sum(VMC)
print "Total actual POD VMC:", sum(POD_VMC)
print "actual umc:", umc
print "Total actual carrying / storage cost:", sum(carry_stg_cost)
print "Total actual lost sales (as POD):", sum(lost_sales_as_POD)
print "Grand total with lost sales:", sum(FMC)+sum(VMC)+sum(POD_VMC)+sum(carry_stg_cost)+sum(lost_sales_as_POD)

# <codecell>

#  Need a stacked bar here
#cost_plot = ggplot(aes(x='Cost Components'), data = plot_df) + \
#    geom_bar(weight = costs) + \
#    ggtitle("10. POD offers the best cost profile.")  + \
#    ylab("Lifetime Cost (dollars)") + \
#    scale_y_continuous(labels='comma')
    
#ggsave(cost_plot, "10_cost_comparison.png")


#N = 4
###plot 10 start###
FMC_plot   = (sum(FMC), sum(FMC_ss), sum(FMC), sum(FMC))
VMC_plot = (sum(VMC), sum(VMC_ss), sum(VMC), sum(VMC))
PODVMC_plot     = (sum(POD_VMC), sum(POD_VMC_ss), sum(POD_VMC), sum(POD_VMC))
carry_storage_plot   = (sum(carry_stg_cost), sum(carry_stg_cost_ss), 
                        sum(carry_stg_cost), sum(carry_stg_cost))
lost_sales_plot = (0, sum(lost_sales_act), 0, 0)
           
POD_plot = (0,0,0, sum(lost_sales_as_POD))
           
ind = np.arange(N)    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence

def dot_sum(*args):
    # pointwise sum of list of tuples
    ans = [0]*len(args[0])
    for arg in args:
        for i, point in enumerate(arg):
            ans[i] += point
    return tuple(ans)
    

### homework: put in a for loop here so that dot_sum isn't terrible
p1 = plt.barh(ind, FMC_plot, width, color='r')
p2 = plt.barh(ind, VMC_plot, width, color='g', left=FMC_plot)
p3 = plt.barh(ind, PODVMC_plot, width, color = 'b', left = dot_sum(VMC_plot, FMC_plot))
p4 = plt.barh(ind, carry_storage_plot, width, color='k', left =
             dot_sum(VMC_plot, FMC_plot, PODVMC_plot))
p5 = plt.barh(ind, lost_sales_plot, width, color='y',
             left = dot_sum(VMC_plot, FMC_plot, PODVMC_plot, carry_storage_plot))
p6 = plt.barh(ind, POD_plot, width, color='m',
             left = dot_sum(VMC_plot, FMC_plot, PODVMC_plot, carry_storage_plot, lost_sales_plot))

plt.xlabel('Cost ($)')

plt.title('10. POD offers the best cost profile.', y=1.05, weight = "bold")
#plt.xticks(np.arange(0,81,10))
plt.yticks(ind+width/2., ('Plan', 'Act w\n Lost Sales', 'Act w\n SS', 'Act w\n POD') )
plt.legend( (p1[0], p2[0],p3[0],p4[0], p5[0], p6[0]), 
           ('FMC', 'VMC', 'POD VMC', 'Carry/Storage', 'Lost Sales', 
            'POD Safety'), loc='upper center', bbox_to_anchor=(0.95, 1.05), ncol=1, fancybox=True, shadow=True)
show_if(10)

# <codecell>

test_columns = ["FMC", "VMC", "VMC POD", "Carry/Stg", "Lost Sales", "LS as POD"]
test_rows = ["Planned", "Act w Lost Sales", "Act w SS", "Act w POD"]


test_df = pd.DataFrame(0,index=test_rows, columns=test_columns)
test_df = test_df.set_value("Planned", 'FMC', sum(FMC))
test_df = test_df.set_value("Planned", 'VMC', sum(VMC))
test_df = test_df.set_value("Planned", 'VMC POD', sum(POD_VMC))
test_df = test_df.set_value("Planned", 'Carry/Stg', sum(carry_stg_cost))
test_df = test_df.set_value("Planned", 'Lost Sales', 0)
test_df = test_df.set_value("Planned", 'LS as POD', 0.)

test_df = test_df.set_value("Act w Lost Sales", 'FMC', sum(FMC))
test_df = test_df.set_value("Act w Lost Sales", 'VMC', sum(VMC))
test_df = test_df.set_value("Act w Lost Sales", 'VMC POD', sum(POD_VMC))
test_df = test_df.set_value("Act w Lost Sales", 'Carry/Stg', sum(carry_stg_cost))
test_df = test_df.set_value("Act w Lost Sales", 'Lost Sales', sum(lost_sales_act))
test_df = test_df.set_value("Act w Lost Sales", 'LS as POD', 0.)

test_df = test_df.set_value("Act w SS", 'FMC', sum(FMC_ss))
test_df = test_df.set_value("Act w SS", 'VMC', sum(VMC_ss))
test_df = test_df.set_value("Act w SS", 'VMC POD', sum(POD_VMC_ss))
test_df = test_df.set_value("Act w SS", 'Carry/Stg', sum(carry_stg_cost_ss))
test_df = test_df.set_value("Act w SS", 'Lost Sales', 0.)
test_df = test_df.set_value("Act w SS", 'LS as POD', 0.)

test_df = test_df.set_value("Act w POD", 'FMC', sum(FMC))
test_df = test_df.set_value("Act w POD", 'VMC', sum(VMC))
test_df = test_df.set_value("Act w POD", 'VMC POD', sum(POD_VMC))
test_df = test_df.set_value("Act w POD", 'Carry/Stg', sum(carry_stg_cost))
test_df = test_df.set_value("Act w POD", 'Lost Sales', 0.)
test_df = test_df.set_value("Act w POD", 'LS as POD', sum(lost_sales_as_POD))

print test_df
test_df.plot(kind='barh', stacked=True, legend=False)
plt.legend(loc='upper center', bbox_to_anchor=(0.95, 1.05), ncol=1,
           fancybox=True, shadow=True)
show_if(11)

#ax = pandas.DataFrame.from_records(d,columns=h)
#ax.plot()
#fig = matplotlib.pyplot.gcf()

# <headingcell level=1>

# 11. POD also allows less expensive low volume printing:

# <markdowncell>

# *	low volume titles
# *	samples
# *	End-of-life
# *	Custom
# *	Illustration

# <headingcell level=1>

# 12. Best results come from using POD with optimization	

# <headingcell level=1>

# 13. You can also reduce variance through better forecasts

# <markdowncell>

# *	show revised area chart with smaller SS

# <headingcell level=1>

# 14. Or reducing lead times

# <markdowncell>

# *	further revised area chart

# <headingcell level=1>

# 15. To do this you need infrastructure:

# <markdowncell>

# *  file mgmt
# *  printers (conventional and POD)
# *  links between OP, MM, and S&OP systems
# *  make this an illustration

# <headingcell level=2>

# To Do list

# <markdowncell>

# * Fixes
#     * fix currency formatting on graphs
#     * fix stacked bar charts
#         *  turn them horizontal
#         *  make sure they actually work
# * Rationalize variables and functions
#     * plan vs actual
#     * lost sales vs. safety stock vs. POD
# * Sensitivity
#     * Book type (get different costs and demand profiles)
#     * Volumes (forecasts, returns)
#     * Bias on forecast
#     * Actual returns with a bias and a variance
#     * Return scrap rate
# * Additions
#     * Expected cost of lost sales to base costs
#         * probability that demand will exceed inventory in period i
#         * by how much?
#         * what's the value?
#     * Obso metric at the end
#     * Actual returns
#     * lifetime demand allocated across periods
#     * express CV as a function of horizon:  proportional to sqrt(hzn)
#     * dynamic planning - recalc of order quantities
#     * planning with expected cost of stockout

