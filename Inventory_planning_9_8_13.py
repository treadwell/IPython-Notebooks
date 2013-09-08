# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <headingcell level=1>

# Forecast Demand

# <codecell>

# Project monthly demand from lifeDemand, trendPerMonth (multiplicative), yearsLife, and
# a list of 12 seasonality coefficients (seasonCoeffs). Return normalized
# demand that gets close to the original lifetime projection. 

def calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs):

    # Calculate level demand
    levelDemand = [float(lifeDemand/yearsLife/12)]* (yearsLife*12)
    
    # Calculate trend demand
    trendDemand = [x * (1+trendPerMonth)**i for i, x in enumerate(levelDemand)]
    
    # Calculate seasonal demand
    seasonalDemand = [x*seasonCoeffs[i % 12] for i, x in enumerate(trendDemand)]

    # Normalize demand to add up to lifetime demand
    d = lifeDemand/sum(seasonalDemand)
    normalizedDemand = [int(round(d*x)) for x in seasonalDemand]
    
    return normalizedDemand

lifeDemand = 24000
trendPerMonth = -.01
yearsLife = 2
seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
#seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,2.0,2.0,2.0,2.0,2.0,2.0]

forecast = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)
print forecast
print sum(forecast)

# <codecell>

# Randomize demand using a normal distribution with a cv that is dependent on number
# of months from origin - not yet implemented
def randomizeDemand(demand):
    cvStart = .015
    cvmonthly = .0015
    pass

# <headingcell level=1>

# Order functions

# <codecell>

def order(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
    # this is the simplistic alternative that you order only what you need
    return forecast[i] 
    

def order_n_months(forecast, i, fmc, perOrder, vmc, interest, startInv=0):  # order n months forward looking demand
    n = 9
    return sum(forecast[i:i+n])
        
def order_lifeEOQ(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
    # order the smaller of EOQ or remaining demand
    # base annual demand from lifetime demand / years in life
    qty = 5000  # default used to kick off umc calculation
    annualDemand = sum(forecast)/len(forecast)*12
    
    # iteratively solve for umc and qty since they're dependent
    for iteration in range(5):
        umc = (fmc + vmc * qty)/qty
        qty = (2*(fmc+perOrder)*annualDemand/interest/umc)**0.5
        #print qty, umc, 
    #print i, sum(forecast[i:])
    if qty < sum(forecast[i:])-startInv:
        return int(qty)
    else:
        return sum(forecast[i:])-startInv  # this needs to take into account the partial period i inventory

def order_trailingEOQ(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
    # order the smaller of EOQ or remaining demand
    # base annual demand from annualized trailing demand, 
    # or lifeEOQ for first period
    qty = 5000
    if i == 0:
        annualDemand = sum(forecast)/len(forecast)*12
    else:
        annualDemand = 12 * sum(forecast[max(0,i-12):i])/len(forecast[max(0,i-12):i])
    for iteration in range(5):                             # iteratively solve for umc and qty since they're dependent
        umc = (fmc + vmc * qty)/qty
        qty = (2*(fmc+perOrder)*annualDemand/interest/umc)**0.5
        #print qty, umc, 
    #print i, sum(forecast[i:])
    if qty < sum(forecast[i:])-startInv:
        return int(qty)
    else:
        return sum(forecast[i:])-startInv # this needs to take into account the partial period i inventory

def order_leadingEOQ(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
    # order the smaller of EOQ or remaining demand
    # base annual demand from annualized forecasted demand
    qty = 5000
    annualDemand = 12 * sum(forecast[i:i+12])/len(forecast[i:i+12])
    
    for iteration in range(5):                             # iteratively solve for umc and qty since they're dependent
        umc = (fmc + vmc * qty)/qty
        qty = (2*(fmc+perOrder)*annualDemand/interest/umc)**0.5
        #print qty, umc, 
    #print i, sum(forecast[i:])
    if qty < sum(forecast[i:])-startInv:
        return int(qty)
    else:
        return sum(forecast[i:])-startInv
        

fmc = 1000       # Fixed manufacturing cost
perOrder = 80.00 # per order cost
vmc = 2.00       # variable manufacturing cost
interest = .12   # WACC for pricing inventory carrying cost
i = 3

lifeDemand = 24000
trendPerMonth = -.00
yearsLife = 2
seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
#seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,2.0,2.0,2.0,2.0,2.0,2.0]

forecast = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)
print forecast
print "simple order: ", order(forecast, i, fmc, perOrder, vmc, interest)
print "order 9 months: ", order_n_months(forecast, i, fmc, perOrder, vmc, interest)
print "order EOQ from lifetime demand: ", order_lifeEOQ(forecast, i, fmc, perOrder, vmc, interest)
print "order EOQ from trailing demand: ", order_trailingEOQ(forecast, i, fmc, perOrder, vmc, interest)
print "order EOQ from forecasted demand: ", order_leadingEOQ(forecast, i, fmc, perOrder, vmc, interest)

# <headingcell level=1>

# Optimizer

# <codecell>

# Calculate guesses in various ways

fmc = 1000       # Fixed manufacturing cost
perOrderCost = 0.00 # per order cost
vmc = 2.00       # variable manufacturing cost
interest = .12   # WACC for pricing inventory carrying cost
i = 3

lifeDemand = 24000
trendPerMonth = -.00
yearsLife = 2
seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]

forecast = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)

def simple_orders(forecast):
    # this is the simplistic alternative that you order only what you need
    orders = forecast
    assert sum(orders)==sum(forecast)
    return orders 

def n_months_orders(forecast):  # order n months forward looking demand
    orders = forecast
    n = 9
    for i, units in enumerate(forecast):
        if i%n == 0:
            orders[i] = sum(forecast[i:i+n])
        else:
            orders[i]=0
    assert sum(orders)==sum(forecast)
    return orders

orders = n_months_orders(forecast)


# <codecell>

bnds = 2* len(orders)*[(0,None)]  # generates bounds on orders and slacks

print bnds

# <headingcell level=1>

# Optimizer with nested functions

# <codecell>

from scipy.optimize import minimize
lifeDemand = 24000
trendPerMonth = -.00
yearsLife = 2
seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
demand = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)

fmc = 10000       # Fixed manufacturing cost
perOrder = 80.00 # per order cost
vmc = 2.00       # variable manufacturing cost
POD_vmc = 5.00   # variable manufacturing cost of POD
interest = .12   # WACC for pricing inventory carrying cost

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
        ending_inventory.append(starting_inventory[i] - demand[i] + orders[i] + POD_orders[i])

        # calculate average inventory in order to calculate period carrying cost
        average_inventory.append((starting_inventory[i]+ending_inventory[i])/2)

    return starting_inventory, ending_inventory, average_inventory

def calculate_POD_orders(orders, fmc, vmc, POD_vmc):
    breakeven = fmc/(POD_vmc - vmc)
    POD_orders = [0] * len(orders)
    for i, order in enumerate(orders):
        if order < breakeven:
            POD_orders[i] = order
            orders[i] = 0
    return orders, POD_orders

def adjusted_orders(orders):
    return [round(max(0, x)) for x in orders]

def calc_order_cost_a(orders, fmc, demand, perOrder, vmc, POD_vmc, interest):
    # function should return total cost

    order = adjusted_orders(orders)
    orders, POD_orders = calculate_POD_orders(orders, fmc, vmc, POD_vmc)

    starting_inventory, ending_inventory, average_inventory = inv_stats(orders, POD_orders, demand)

    # calculate costs
    # need blended cost if there were a POD order

    fixed_cost = [fmc + perOrder if order else 0 for order in orders]
    variable_cost = [vmc * order for order in orders]
    POD_variable_cost = [POD_vmc * POD_order for POD_order in POD_orders]

    try:
        umc = (sum(fixed_cost)+sum(variable_cost)+sum(POD_variable_cost)) / (sum(orders)+sum(POD_orders))
    except ZeroDivisionError:
        return 0


    carrying_cost = [float(interest) / 12 * month_avg * umc for month_avg in average_inventory] 

    total_cost = sum(fixed_cost + variable_cost + POD_variable_cost + carrying_cost)

    return total_cost

assert calc_order_cost_a([0, 0, 0, 0], 1000, [0, 0, 0, 0], 1000, 1, 5, .12) == 0
assert calc_order_cost_a([1000, 1000, 1000, 1000], 1000, [1000, 1000, 1000, 1000], 1000, 1, 5, .12) == 12000.0
assert calc_order_cost_a([100, 100, 100, 100], 1000, [100, 100, 100, 100], 1000, 1, 5, .12) == 2000.0


def optimize_order_cost(fmc, demand, perOrder, vmc, POD_vmc, interest, guess, method):

    def inner_calc_order_cost_a(orders):
        return calc_order_cost_a(orders, fmc, demand, perOrder, vmc, POD_vmc, interest)
    
    opt =  minimize(inner_calc_order_cost_a, guess, method = method)
    print opt
    print "min cost: %s" %opt['fun']
    print "optimal schedule: %s" %adjusted_orders(opt['x'])


print "Powell, guess simple order:", optimize_order_cost(fmc, demand, perOrder, vmc, POD_vmc, interest, demand, method = 'Powell')

print "Powell, guess 0 orders:", optimize_order_cost(fmc, demand, perOrder, vmc, POD_vmc, interest, [0] * len(demand), method = 'Powell')

assert len(demand) %2 == 0
print "Powell, guess 0 orders:", optimize_order_cost(fmc, demand, perOrder, vmc, POD_vmc, interest, ([12000] + [0] * (len(demand)/2 -1))*2, method = 'Powell')

#print "Powell, guess EOQ"
#print "Powell, order 9 months"

# <codecell>

# to do:
# 1. This looks like costs are being handled correctly, but the x values are definitely not showing correctly
#    a.  It looks like the x values are ignoring the POD or any overrides
#    b.  Optimization should return the exact profile of orders and POD_orders that optimizes cost
# 2. Should this be a different algorithm with explicit bounds? Should it optimize POD_orders, too?

# 3. asserts to check code
# 4. improvements to code - review the structure of the code
# 5. graphs to show what's going on
# 6. tie to optimization
# 7. update to handle POD
# 8. show output for different approaches
#    a. scenarios run
#    b. total cost of each
#    c. collapsed inventory plan showing printings and associated periods
# 9. include randomization
#    a. bias in lifetime forecast
#    b. bias in monthly forecast
#    c. variance in monthly forecast
# 10. run for many titles simultaneously

