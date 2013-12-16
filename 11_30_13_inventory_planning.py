# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from ggplot import *
import pandas as pd
import numpy as np
from scipy import stats

# <headingcell level=1>

# 1. Start with a forecast of demand

# <codecell>

# Start with a forecast of demand

month = [i+1 for i in xrange(36)]

level = [1000] * 36

trendPerMonth = -0.05
trend = [int(x * (1+trendPerMonth)**i) for i, x in enumerate(level)]

seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
forecast = [int(x*seasonCoeffs[i % 12]) for i, x in enumerate(trend)]

df = pd.DataFrame(month, columns=['month'])
df['level'] = level
df['trend'] = trend
df['forecast'] = forecast

forecast_plot = ggplot(aes(x='month', y='forecast'), data=df) + \
    geom_line(size = 4) + \
    ggtitle("1. Start with a forecast of demand...") + \
    xlab("Month") + \
    ylab("Demand (units)")

ggsave(forecast_plot, "01_forecast.png")
#plt.show(1)

# <headingcell level=1>

# 2. ...and a forecast of returns

# <codecell>

returns_rate = 0.2
lag = 3

returns = [returns_rate*x for x in forecast]  # add lag

#  Note: replace this with a direct pandas calculation

def calc_returns(sales):
    returns = [None] * len(sales)
    for i, x in enumerate(returns):
        if i > lag-1:
            returns[i] = int(sales[i-lag]* returns_rate)
    return returns
     
df['returns'] = calc_returns(forecast)

# plot two lines: forecast and returns

graph_this = pd.melt(df[['month', 'forecast', 'returns']], id_vars='month')

returns_plot = ggplot(aes(x='month', y='value', colour='variable'), data=graph_this) + \
    geom_line(size = 4) + \
    ggtitle("2. ...and a forecast of returns.") + \
    xlab("Month") + \
    ylab("Units")

ggsave(returns_plot, "02_returns.png")
#plt.show(2)

# <headingcell level=1>

# 3. use planned purchases, demand, and returns to calculate inventory position...

# <codecell>

def n_months_orders(forecast):  # order n months forward looking demand
    orders = [0] * len(forecast)
    n = 9
    for i, units in enumerate(forecast):
        if i%n == 0:
            orders[i] = sum(forecast[i:i+n])
        else:
            orders[i]=0
    assert sum(orders)==sum(forecast)
    return orders

orders = n_months_orders(forecast)

df['orders'] = orders
POD_orders = [0] * len(forecast)
df['POD_orders'] = POD_orders


def inv_stats(orders, POD_orders, demand):
    starting_inventory = []
    ending_inventory = []
    average_inventory = []

    for i, order in enumerate(orders):
        # calculate starting inventory
        if i == 0:
            starting_inventory.append(0)  # eventually replace this with an optional input
        else:
            starting_inventory.append(ending_inventory[i-1])
        
        # calculate ending inventory from inventory balance equation
        ending_inventory.append(max(0,starting_inventory[i] - demand[i] + orders[i] + POD_orders[i]))

        # calculate average inventory in order to calculate period carrying cost
        average_inventory.append((starting_inventory[i]+ending_inventory[i])/2)

    return starting_inventory, ending_inventory, average_inventory

start_inv, end_inv, avg_inv = inv_stats(orders, POD_orders, forecast)


df['start_inv'] = start_inv
df['end_inv'] = end_inv
df['avg_inv'] = avg_inv

# This needs to be an area chart

inventory_plot = ggplot(aes(x='month', y='end_inv',), data=df) + \
    geom_line(size=4) + \
    ggtitle("3. Use planned purchases, demand, and returns to calculate inventory position...") + \
    xlab("Month") + \
    ylab("Ending Inventory (units)")
    
ggsave(inventory_plot, "03_inventory.png")
#plt.show(3)

# <headingcell level=1>

# 4. ...yielding a lifetime expected cost.

# <codecell>

# Fixed manufacturing cost - fmc
# per order cost - perOrder
# variable manufacturing cost - vmc
# variable manufacturing cost of POD - POD_vmc
# WACC for pricing inventory carrying cost - WACC

cost = {'perOrder': 80.0, 'WACC': 0.12, 'POD_vmc': 5.0, 'fmc': 1000, 'vmc': 2.0, 'lost_margin': 20.00}

FMC = [cost['fmc'] + cost['perOrder'] if round(order) else 0 for order in orders]
VMC = [cost['vmc'] * order for order in orders]
POD_VMC = [cost['POD_vmc'] * POD_order for POD_order in POD_orders]
umc = (sum(FMC)+sum(VMC)+sum(POD_VMC)) / (sum(orders)+sum(POD_orders)) # approximation - should be a list
carry_stg_cost = [float(cost['WACC']) / 12 * month_avg * umc for month_avg in avg_inv] 

print "Total FMC:", sum(FMC)
print "Total VMC:", sum(VMC)
print "Total POD VMC:", sum(POD_VMC)
print "umc:", umc
print "Total carrying / storage cost:", sum(carry_stg_cost)

df['FMC'] = FMC
sum_FMC = sum(FMC)

costsdf = pd.DataFrame([sum_FMC], columns=['sum_FMC'])
costsdf['sum_VMC'] = [sum(VMC)]
costsdf['sum_POD_VMC'] = [sum(POD_VMC)]
costsdf['sum_carry_stg_cost'] = [sum(carry_stg_cost)]
#df = pd.DataFrame(month, columns=['month'])

#bar_data = pd.melt(df[['FMC', 'VMC', 'POD_VMC', 'carry_stg_cost']])

to_plot = ['FMC']

## values in costdf, passed to ggplot, are *labels*
## values in costdf, passed to weight, are what's actually graphed
## the dataframe passed to ggplot should look like: ['FMC', 'VMC', 'etc']
## pass weight a list [sum(FMC), sum(VMC), sum(etc)]
plot_df = pd.DataFrame(['FMC', 'VMC', 'POD_VMC'], columns = ['X axis label'])

cost_plot = ggplot(aes(x='X axis label'), data = plot_df) + \
    geom_bar(weight = [4000, 3000, 55], position = 'stack') + \
    ggtitle("4. ...yielding a lifetime expected cost.") 

## from geom_bar class implementation: valid keywords are
## VALID_AES = ['x', 'color', 'alpha', 'fill', 'label', 'weight']
## stacked bar chart: http://matplotlib.org/examples/pylab_examples/hatch_demo.html
## http://matplotlib.org/examples/pylab_examples/histogram_demo_extended.html
## prettyplotlib: http://blog.olgabotvinnik.com/post/58941062205/prettyplotlib-painlessly-create-beautiful-matplotlib



    # Generate data
#c <- ggplot(mtcars, aes(factor(cyl)))

# By default, uses stat="bin", which gives the count in each category
#c + geom_bar()
ggsave(cost_plot, "04_cost.png")
plt.show(3)

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

#print "sd_forecast:", sd_forecast
#print "demand:", demand
#print "lower_CI", lower_CI
#print "upper_CI", upper_CI

# plot 4 lines: forecast, upper_CI, lower_CI and demand

df['demand'] = demand
df['upper_CI'] = upper_CI
df['lower_CI'] = lower_CI

graph_this = pd.melt(df[['month', 'forecast', 'demand', 'upper_CI', 'lower_CI']], id_vars='month')

returns_plot = ggplot(aes(x='month', y='value', colour='variable'), data=graph_this) + \
    geom_line(size = 4) + \
    ggtitle("5. But forecasts are wrong...") + \
    xlab("Month") + \
    ylab("Units")

ggsave(returns_plot, "05_forecast_error.png")
#plt.show(5)

# <headingcell level=1>

# 6. ...leading to stockouts with lost sales and expediting...

# <codecell>

start_inv_act = []
start_inv_posn_act = []
end_inv_act = []
end_inv_posn_act = []
avg_inv_act = []

for i, order in enumerate(orders):
    # calculate starting inventory
    if i == 0:
        start_inv_act.append(0)  # eventually replace this with an optional input
        start_inv_posn_act.append(0)
    else:
        start_inv_act.append(end_inv_act[i-1])
        start_inv_posn_act.append(end_inv_posn_act[i-1])
        
    # calculate ending inventory from inventory balance equation
    end_inv_act.append(max(0,start_inv_act[i] - demand[i] + orders[i] + POD_orders[i]))
    end_inv_posn_act.append(start_inv_posn_act[i] - demand[i] + orders[i] + POD_orders[i])

    # calculate average inventory in order to calculate period carrying cost
    avg_inv_act.append((start_inv_act[i]+end_inv_act[i])/2)

#print 'start_inv_act', start_inv_act
#print 'start_inv_posn_act', start_inv_posn_act
#print 'end_inv_act', end_inv_act
#print 'end_inv_posn_act', end_inv_posn_act
#print 'avg_inv_act', avg_inv_act

df['start_inv_act'] = start_inv_act
df['start_inv_posn_act'] = start_inv_posn_act
df['end_inv_act'] = end_inv_act
df['end_inv_posn_act'] = end_inv_posn_act
df['avg_inv_act'] = avg_inv_act

# This needs to be an area chart

inventory_plot = ggplot(aes(x='month', y='end_inv_posn_act',), data=df) + \
    geom_line(size=4) + \
    ggtitle("6. ...leading to stockouts with lost sales and expediting...") + \
    xlab("Month") + \
    ylab("Ending Inventory Position(units)")
    
ggsave(inventory_plot, "06_inventory_posn.png")

#print inventory_plot
#plt.show(3)

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

# <headingcell level=1>

# 8. The usual approach to avoid lost sales is to carry safety stock

# <codecell>

#   Area chart with cycle and safety stock
#   normal z value for percent, mean?, sd?
safety_stock = [0]*len(forecast)

# <headingcell level=1>

# 9. Another is to use POD (show with an alternative cost model)

# <codecell>

	
#	 - it looks like lost sales, but is cheaper
#  put the lost sales numbers into the POD vector and recalc positions and costs
revalued_lost_sales = [0]*len(forecast)

# <headingcell level=1>

# 10. POD is best (show stacked bars of the three alternatives)

# <headingcell level=1>

# 11. POD also allows less expensive low volume printing:

# <rawcell>

# #	samples
# #	EOL
# #	Custom

# <headingcell level=1>

# 12. Best results come from using POD with optimization	

# <headingcell level=1>

# 13. You can also reduce variance through better forecasts

# <rawcell>

# # show revised area chart with smaller SS

# <headingcell level=1>

# 14. Or reducing lead times

# <rawcell>

# # further revised area chart

# <headingcell level=1>

# 15. To do this you need infrastructure:

# <rawcell>

# 	
# #	file mgmt
# #	printers (conventional and POD)
# #	links between OP, MM, and S&OP systems

# <markdowncell>

# Modifications:
# * Actual returns with a bias and a variance
# * Bias on forecast
# * Return scrap rate
# * Obso metric at the end
# * express CV as a function of horizon:  proportional to sqrt(hzn)
# * Use the inline graphing statement for ipnb
# 
# Planning approaches
# * dynamic planning - recalc of order quantities
# * planning with expected cost of stockout
# 
# Facets
# * Use combinations of parameters and planning approaches

