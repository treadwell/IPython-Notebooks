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

#forecast = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)
#print forecast
#print sum(forecast)

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
#print forecast
#print "simple order: ", order(forecast, i, fmc, perOrder, vmc, interest)
#print "order 9 months: ", order_n_months(forecast, i, fmc, perOrder, vmc, interest)
#print "order EOQ from lifetime demand: ", order_lifeEOQ(forecast, i, fmc, perOrder, vmc, interest)
#print "order EOQ from trailing demand: ", order_trailingEOQ(forecast, i, fmc, perOrder, vmc, interest)
#print "order EOQ from forecasted demand: ", order_leadingEOQ(forecast, i, fmc, perOrder, vmc, interest)

# <headingcell level=1>

# Heuristics

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
    # only order what you need in the period
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

def lowest_period_cost_orders(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
    # calculate cost for n periods into the future.  Choose the n that gives lowest cost per unit
    pass

orders = n_months_orders(forecast)


# <headingcell level=1>

# Optimizer with nested functions

# <codecell>

from scipy.optimize import minimize
lifeDemand = 24000
trendPerMonth = -.00
yearsLife = 2
seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
#demand = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)

demand = 12 * [1000]
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
        ending_inventory.append(max(0,starting_inventory[i] - demand[i] + orders[i] + POD_orders[i]))

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

def adjusted_orders(orders, demand):
    orders = [max(0, x) for x in orders]
    #orders[0] = max(sum(demand) - sum(orders[1:]),0)
    return orders

def calc_order_cost_a(orders, fmc, demand, perOrder, vmc, POD_vmc, interest):
    # function should return total cost
    #orders = adjusted_orders(orders, demand)
    
    orders, POD_orders = calculate_POD_orders(orders, fmc, vmc, POD_vmc)

    starting_inventory, ending_inventory, average_inventory = inv_stats(orders, POD_orders, demand)

    # calculate costs

    fixed_cost = [fmc + perOrder if round(order) else 0 for order in orders]
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
assert calc_order_cost_a(24*[1000], 10000, 24*[1000], 80, 2, 5, .12) == 120000.0

assert calc_order_cost_a([4000, 0, 0, 0], 1000, [0, 0, 0, 0], 1000, 1, 5, .12) == 6140.0
assert calc_order_cost_a([4000, 0, 0, 0], 0, [0, 0, 0, 0], 0, 1, 5, 12) == 18000.0

# <headingcell level=2>

# Calculate contraints and bounds

# <codecell>

# I don't understand this at all

def c(i):
    def inner_c(guess):
        try:
            return guess[i]
        except IndexError:
            return 0
    return inner_c

# print c(1)

def 4th_order(guess):
    return guess[4]

4th_order = c(4)

order[4] == 4th_order(order) == c(4)(order) ## c(4) is a function

# <codecell>

def calculate_bounds(method, demand):
    if method == "SLSQP":
        return len(demand)*[(0,None)]
        #return tuple(len(demand)*[(0,None)])
    return None

#assert calculate_bounds('SLSQP', [100, 100, 100]) == ((0, None), (0, None), (0, None))

def c(i):
    def inner_c(guess):
        try:
            return guess[i]
        except IndexError:
            return 0
    return inner_c

# c is analagous to copy in the loop below


def c(i):
    def inner_c():
        return i
    return inner_c

any_name = c(4) # what's inner_c called? anything
# key point: i is converted to a constant

counter = []
## print counter and copy and see what happens
for i in xrange(5):
    counter.append('anything') # can append anything
    #copy = list(counter)
    def myfun():
        return len(counter)

    def myfun2():
        return len(list(counter)) # copy of counter
  #  def myfun():
  #      return 4


loop 1:
        counter = [0]
        unnamed_copy = [0]
        myfun: return len(counter)
        myfun2: return len(unnamed_copy)
loop 2:
        counter = [0, 0]
        unnamed_copy_2 = [0, 0]
        ## important
        unnamed_copy = [0] # from the previous loop
        new myfun: return len(counter) # returns 2
        old myfun: return len(counter) # returns 2
        new myfun2: return len(unnamed_copy_2) # returns 2
        old myfun2: return len(unnamed_copy) # returns 1!
  

def f(counter):
    return len(counter)

#f = len # same as above
    
def f():
    return len(counter)
    
def calculate_constraints(method, demand):
    if method == "COBYLA" or method == "SLSQP":
        ans = [{'type': 'ineq', 'fun': lambda orders: sum(orders[:1]) - sum(demand[:1])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:2]) - sum(demand[:2])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:3]) - sum(demand[:3])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:4]) - sum(demand[:4])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:5]) - sum(demand[:5])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:6]) - sum(demand[:6])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:7]) - sum(demand[:7])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:8]) - sum(demand[:8])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:9]) - sum(demand[:9])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:10]) - sum(demand[:10])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:11]) - sum(demand[:11])},
               {'type': 'ineq', 'fun': lambda orders: sum(orders[:12]) - sum(demand[:12])},
               {'type': 'ineq', 'fun': lambda orders: orders[0]}]
#        if method == "SLSQP":
#            return ans
#    if method == "COBYLA":
#        for i in range(len(demand)):
#            constraint = {'type': 'ineq', 'fun': c(i)}
#            ans.append(constraint)
        return ans
    return None

#  {'type': 'ineq', 'fun': lambda orders: sum(orders[:1]) - sum(demand[:1])}

#print len(calculate_constraints('SLSQP', [100, 100, 100]))
#print len(calculate_constraints('COBYLA', [100, 100, 100]))
#[0]['fun']([100, 100, 100]) == 0
 
#print calculate_constraints('COBYLA', [100, 100, 100])[1]['fun']([100, 100, 100]) == 0
#print calculate_constraints('COBYLA', [100, 100, 100])[2]['fun']([100, 100, 100]) == 0
#print calculate_constraints('COBYLA', [100, 100, 100])[24]['fun']([100, 100, 100]) == 0
#print calculate_constraints('COBYLA', [100, 100, 100])[47]['fun']([100, 100, 100]) == 0

#print calculate_constraints('COBYLA', [0, 0, 0])[0]['fun']([100, 100, 100]) == 100
#print calculate_constraints('COBYLA', [0, 0, 0])[1]['fun']([100, 100, 100]) == 200
#print calculate_constraints('COBYLA', [0, 0, 0])[2]['fun']([100, 100, 100]) == 300

#print calculate_constraints('COBYLA', [100, 100, 100])[0]['fun']([0, 0, 0]) == -100
#print calculate_constraints('COBYLA', [100, 100, 100])[1]['fun']([0, 0, 0]) == -200
#print calculate_constraints('COBYLA', [100, 100, 100])[2]['fun']([0, 0, 0]) == -300


# <codecell>

def optimize_order_cost(fmc, demand, perOrder, vmc, POD_vmc, interest, guess, method, bounds=None, constraints=None):

    def inner_calc_order_cost_a(orders):
                return calc_order_cost_a(orders, fmc, demand, perOrder, vmc, POD_vmc, interest)
    
    opt =  minimize(inner_calc_order_cost_a, guess, method = method, 
        bounds=calculate_bounds(method, demand),
        constraints=calculate_constraints(method, demand), 
        options = {'maxiter':50000})
    
    #print opt
    
    print "success: %s" %opt['success']
    print "message: %s" %opt['message']
    print "min cost: %s" %opt['fun']
    print "optimal schedule: %s" %opt['x']

print "COBYLA, guess simple order:", optimize_order_cost(fmc, tuple(demand), perOrder, vmc, POD_vmc, 
    interest, demand, method = 'COBYLA')

print "COBYLA, guess 0 orders:", optimize_order_cost(fmc, demand, perOrder, vmc, POD_vmc, 
    interest, [0] * len(demand), method = 'COBYLA')

#assert len(demand) %2 == 0
#print "COBYLA, guess two equal orders:", optimize_order_cost(fmc, demand, perOrder, vmc, POD_vmc, 
#    interest, ([sum(demand)/2] + [0] * (len(demand)/2 -1))*2, method = 'COBYLA')

# <codecell>

# to do:
# 1. Try SLSQP
#    a.  bnds (0,None)
#    b.  constraints: sum(orders[:i]) >= sum(demand[:i])
#    c.  what does bnderr = where(bnds[:, 0] > bnds[:, 1])[0]   mean?
# 2. Try all of the common guesses: EOQ, 9 months, etc.
# 3. graphs to show what's going on
# 4. show output for different approaches
#    a. scenarios run
#    b. total cost of each
#    c. collapsed inventory plan showing printings and associated periods
# 5. include randomization
#    a. bias in lifetime forecast
#    b. bias in monthly forecast
#    c. variance in monthly forecast
# 6. run for many titles simultaneously

# <codecell>

print "Calculating"
# print "SLSQP, guess simple order:", optimize_order_cost(fmc, demand,
# perOrder, vmc, POD_vmc, interest, demand, method = 'SLSQP')


def f(x):
    # x is a tuple of 2 numbers
    return x[0]**2 + x[1]**2

fun = lambda x: (x[0] - 1)**2 + (x[1] - 2.5)**2

cons = ({'type': 'ineq', 'fun': lambda x:  x[0] - 2 * x[1] + 2},
        {'type': 'ineq', 'fun': lambda x: -x[0] - 2 * x[1] + 6},
        {'type': 'ineq', 'fun': lambda x: -x[0] + 2 * x[1] + 2})

bnds = ((0, None), (0, None))

opt = minimize(fun, (2, 0), method='SLSQP', bounds=bnds,
               constraints=cons, options = {'maxiter':10000})

print "success: %s" %opt['success']
print "message: %s" %opt['message']
print "min cost: %s" %opt['fun']
print "optimal schedule: %s" %opt['x']

# <codecell>


# <codecell>

# simple COBYLA
from scipy.optimize import minimize

def f(x):
    # x is a tuple of 2 numbers
    return x[0]**2 + x[1]**2

cons = ({'type': 'ineq', 'fun': lambda x:  x[0] + x[1]-4},
        {'type': 'ineq', 'fun': lambda x:  x[0]-1},
        {'type': 'ineq', 'fun': lambda x:  x[1]-1})


opt = minimize(f, (15, 15), method='COBYLA',
               constraints=cons, options = {'maxiter':10000})

print "success: %s" %opt['success']
print "message: %s" %opt['message']
print "min cost: %s" %opt['fun']
print "optimal schedule: %s" %opt['x']

# <codecell>

# more complex COBYLA

from scipy.optimize import minimize

y = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]

def f(x):
    cost = sum(element**i for i, element in enumerate(x))
    # x is a tuple of n numbers
    return cost

cons = ({'type': 'ineq', 'fun': lambda x:  sum(x) - sum(y)},
        {'type': 'ineq', 'fun': lambda x:  x[0]},
        {'type': 'ineq', 'fun': lambda x:  x[1]})

guess = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


opt = minimize(f, guess, method='COBYLA',
               constraints=cons, options = {'maxiter':1000})

print "success: %s" %opt['success']
print "message: %s" %opt['message']
print "min cost: %s" %opt['fun']
print "optimal schedule: %s" %opt['x']

# <codecell>


