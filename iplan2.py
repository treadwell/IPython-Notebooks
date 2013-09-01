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
    #print "levelDemand"
    #print levelDemand
    
    # Calculate trend demand
    trendDemand = [x * (1+trendPerMonth)**i for i, x in enumerate(levelDemand)]
    #print trendDemand
    #print trendDemand
    
    # Calculate seasonal demand
    seasonalDemand = [x*seasonCoeffs[i % 12] for i, x in enumerate(trendDemand)]
    #print "seasonalDemand"
    #print seasonalDemand
    #print sum(seasonalDemand)

    # Normalize demand to add up to lifetime demand
    d = lifeDemand/sum(seasonalDemand)
    normalizedDemand = [int(round(d*x)) for x in seasonalDemand]
    #print "normalizedDemand"
    #print normalizedDemand
    #print sum(normalizedDemand)
    
    return normalizedDemand

# lifeDemand = 24000
# trendPerMonth = -.01
# yearsLife = 2
# seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
# #seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,2.0,2.0,2.0,2.0,2.0,2.0]

# forecast = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)
# print forecast
# print sum(forecast)

# # <codecell>

# # Randomize demand using a normal distribution with a cv that is dependent on number
# # of months from origin - not yet implemented
# def randomizeDemand(demand):
#     cvStart = .015
#     cvmonthly = .0015
#     pass

# # <headingcell level=1>

# # Order functions

# # <codecell>

# def order(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
#     # this is the simplistic alternative that you order only what you need
#     return forecast[i] 
    

# def order_n_months(forecast, i, fmc, perOrder, vmc, interest, startInv=0):  # order n months forward looking demand
#     n = 9
#     return sum(forecast[i:i+n])
        
# def order_lifeEOQ(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
#     # order the smaller of EOQ or remaining demand
#     # base annual demand from lifetime demand / years in life
#     qty = 5000  # default used to kick off umc calculation
#     annualDemand = sum(forecast)/len(forecast)*12
    
#     # iteratively solve for umc and qty since they're dependent
#     for iteration in range(5):
#         umc = (fmc + vmc * qty)/qty
#         qty = (2*(fmc+perOrder)*annualDemand/interest/umc)**0.5
#         #print qty, umc, 
#     #print i, sum(forecast[i:])
#     if qty < sum(forecast[i:])-startInv:
#         return int(qty)
#     else:
#         return sum(forecast[i:])-startInv  # this needs to take into account the partial period i inventory

# def order_trailingEOQ(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
#     # order the smaller of EOQ or remaining demand
#     # base annual demand from annualized trailing demand, 
#     # or lifeEOQ for first period
#     qty = 5000
#     if i == 0:
#         annualDemand = sum(forecast)/len(forecast)*12
#     else:
#         annualDemand = 12 * sum(forecast[max(0,i-12):i])/len(forecast[max(0,i-12):i])
#     for iteration in range(5):                             # iteratively solve for umc and qty since they're dependent
#         umc = (fmc + vmc * qty)/qty
#         qty = (2*(fmc+perOrder)*annualDemand/interest/umc)**0.5
#         #print qty, umc, 
#     #print i, sum(forecast[i:])
#     if qty < sum(forecast[i:])-startInv:
#         return int(qty)
#     else:
#         return sum(forecast[i:])-startInv # this needs to take into account the partial period i inventory

# def order_leadingEOQ(forecast, i, fmc, perOrder, vmc, interest, startInv=0):
#     # order the smaller of EOQ or remaining demand
#     # base annual demand from annualized forecasted demand
#     qty = 5000
#     annualDemand = 12 * sum(forecast[i:i+12])/len(forecast[i:i+12])
    
#     for iteration in range(5):                             # iteratively solve for umc and qty since they're dependent
#         umc = (fmc + vmc * qty)/qty
#         qty = (2*(fmc+perOrder)*annualDemand/interest/umc)**0.5
#         #print qty, umc, 
#     #print i, sum(forecast[i:])
#     if qty < sum(forecast[i:])-startInv:
#         return int(qty)
#     else:
#         return sum(forecast[i:])-startInv
        

# fmc = 1000       # Fixed manufacturing cost
# perOrder = 80.00 # per order cost
# vmc = 2.00       # variable manufacturing cost
# interest = .12   # WACC for pricing inventory carrying cost
# i = 3

# lifeDemand = 24000
# trendPerMonth = -.00
# yearsLife = 2
# seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
# #seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,2.0,2.0,2.0,2.0,2.0,2.0]

# forecast = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)
# print forecast
# print "simple order: ", order(forecast, i, fmc, perOrder, vmc, interest)
# print "order 9 months: ", order_n_months(forecast, i, fmc, perOrder, vmc, interest)
# print "order EOQ from lifetime demand: ", order_lifeEOQ(forecast, i, fmc, perOrder, vmc, interest)
# print "order EOQ from trailing demand: ", order_trailingEOQ(forecast, i, fmc, perOrder, vmc, interest)
# print "order EOQ from forecasted demand: ", order_leadingEOQ(forecast, i, fmc, perOrder, vmc, interest)

# # <headingcell level=1>

# # Inventory Planning (reference only)

# # <codecell>

# # From starting inventory and a demand forecast, determine the cost implications of various inventory planning approaches.
# # These approaches will call on different print planning algorithms:
# #     Algorithm  extension
# #     ---------  ----------------
# #     As Needed  no POD
# #     9-months   with and without POD
# #     EOQ        with and without POD
# #     optimal    with and without POD (using SciPy tools)
# #

# def inventory_plan(demand, fmc, perOrder, vmc, vmcPOD, interest, order_function=order):
#     # function should return total cost and 2 arrays:  conventional units per month and POD units per month
#     #
#     # This function is being refactored
#     #
#     invStart = []
#     invEnd = []
#     invAvg = []
#     orders = []
#     ordersPOD = []
#     costFixed = []
#     costVariable = []
#     costVariablePOD = []
#     costCarrying = []
#     cost = []
#     costTotal = 0
#     for i in range(len(demand)):
#         # calculate starting inventory
#         if i ==0:
#             invStart.append(0)  # eventually replace this with an optional input
#         else:
#             invStart.append(invEnd[i-1])
        
#         # triggers an order if there's not enough inventory in a period to satisfy demand
#         if demand[i] > invStart[i]: 
#             startInv = invStart[i]  # used to avoid overprinting this amount at end of life
#             qty = order_function(forecast, i, fmc, perOrder, vmc, interest, startInv)
#             if fmc + vmc * qty < vmcPOD * qty:   # this really should have carry cost, too
#                 orders.append(qty)
#                 ordersPOD.append(0)
#             else:
#                 orders.append(0)
#                 ordersPOD.append(qty)
#         else:
#             orders.append(0)
#             ordersPOD.append(0)
        
#         # calculate ending inventory from inventory balance equation
#         invEnd.append(invStart[i] - demand[i] + orders[i] + ordersPOD[i])
    
#         # calculate average inventory in order to calculate period carrying cost
#         invAvg.append((invStart[i]+invEnd[i])/2)
    
#         # calculate costs
#         # need blended cost if there were a POD order
#         if orders[i] > 0:
#             costFixed.append(fmc + perOrder)        # fixed manufacturing cost
#             costVariable.append(vmc * orders[i])    # variable manufacturing cost
#             costVariablePOD.append(0)
#         elif ordersPOD[i] > 0:
#             costVariablePOD.append(vmcPOD * ordersPOD[i])    # variable manufacturing cost for POD
#             costFixed.append(0)
#             costVariable.append(0)
#         else:
#             costFixed.append(0)
#             costVariable.append(0)
#             costVariablePOD.append(0)
#         # unit manufacturing cost in order to calculate period carrying cost
#         # this could be enhanced to be FIFO
#         umc = (sum(costFixed)+sum(costVariable)+sum(costVariablePOD)) / (sum(orders) + sum(ordersPOD))
#         costCarrying.append((interest/12) * invAvg[i] * umc)           # calculate carrying cost
#         cost.append(costFixed[i] + costVariable[i] + costCarrying[i] + costVariablePOD[i])  # calculate total cost per period
#         costTotal += cost[i]                                           # accumulate total cost
    
#     #print "demand: ", demand
#     #print "orders: ", orders
#     #print "invStart: ", invStart
#     #print "invEnd: ", invEnd
#     #print "invAvg: ", invAvg
#     #print "costFixed: ", costFixed
#     #print "costVariable: ", costVariable
#     #print "costCarrying: ", costCarrying
#     #print "costTotal: ", costTotal
    
#     return costTotal, orders, ordersPOD

# # <headingcell level=1>

# # Optimizer

# # <codecell>

# # bnds = 2* len(orders)*[(0,None)]  # generates bounds on orders and slacks

# # print bnds

# # <codecell>

# # strategy:  get optimizer working with just conventional, then expand to POD

# fmc = 1000       # Fixed manufacturing cost
# perOrderCost = 0.00 # per order cost
# vmc = 2.00       # variable manufacturing cost
# interest = .12   # WACC for pricing inventory carrying cost
# i = 3

# lifeDemand = 24000
# trendPerMonth = -.00
# yearsLife = 2
# seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]

# forecast = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)

# def simple_orders(forecast):
#     # this is the simplistic alternative that you order only what you need
#     orders = forecast
#     assert sum(orders)==sum(forecast)
#     return orders 

# def n_months_orders(forecast):  # order n months forward looking demand
#     orders = forecast
#     n = 9
#     for i, units in enumerate(forecast):
#         if i%n == 0:
#             orders[i] = sum(forecast[i:i+n])
#         else:
#             orders[i]=0
#     assert sum(orders)==sum(forecast)
#     return orders

# orders = n_months_orders(forecast)

# def calc_order_cost(demand, orders, fmc, perOrderCost, vmc, interest):
#     # function should return total cost
#     invStart = []
#     invEnd = []
#     invAvg = []
#     costFixed = []
#     costVariable = []
#     costCarrying = []
#     cost = []
#     costTotal = 0
    
#     for i, order in enumerate(orders):
#         # calculate starting inventory
#         if i ==0:
#             invStart.append(0)  # eventually replace this with an optional input
#         else:
#             invStart.append(invEnd[i-1])
        
#         # calculate ending inventory from inventory balance equation
        
#         invEnd.append(invStart[i] - demand[i] + orders[i])
    
#         # calculate average inventory in order to calculate period carrying cost
#         invAvg.append((invStart[i]+invEnd[i])/2)
    
#         # calculate costs
#         # need blended cost if there were a POD order
#         if order > 0:
#             costFixed.append(fmc + perOrderCost)        # fixed manufacturing cost
#             costVariable.append(vmc * order)    # variable manufacturing cost
#         else:
#             costFixed.append(0)
#             costVariable.append(0)
#         # unit manufacturing cost in order to calculate period carrying cost
#         # this could be enhanced to be FIFO
#         umc = (sum(costFixed)+sum(costVariable)) / (sum(orders))
#         costCarrying.append((interest/12) * invAvg[i] * umc)           # calculate carrying cost
#         cost.append(costFixed[i] + costVariable[i] + costCarrying[i])  # calculate total cost per period
#         costTotal += cost[i]                                           # accumulate total cost
    
#     #print "demand: ", units
#     #print "orders: ", orders
#     #print "invStart: ", invStart
#     #print "invEnd: ", invEnd
#     #print "invAvg: ", invAvg
#     #print "costFixed: ", costFixed
#     #print "costVariable: ", costVariable
#     #print "costCarrying: ", costCarrying
#     #print "costTotal: ", costTotal
    
#     return costTotal

# print calc_order_cost(forecast, orders, fmc, perOrderCost, vmc, interest)


# #  These others aren't baked yet

# from scipy.optimize import minimize

# #res = minimize(calc_order_cost, forecast, method='Anneal', bounds=bnds)

# #res = minimize(calc_order_cost, order_guess, method='Anneal', bounds=bnds)

# # pass in orders for month 2-n
# #calcualte orders for month 1
# #first-month = sum(forecast) - sum orders_2_thru_n)
# #all_orders = [first_month] + orders_2_thru_n

# def calc_orders(demand, costs):
#     #calculate orders
#     orders = []
#     return orders

# def calc_orders_POD(demand, costs, orders):
#     #calculate POD orders
#     orders_POD = []
#     return orders_POD

# def calc_POD_cost(orders_POD):
#     POD_order_cost = 0
#     return POD_order_cost

# def calc_total_cost(order_cost, POD_order_cost):
#     return order_cost + POD_order_cost

# # <headingcell level=1>

# # Optimizer with nested functions

# # <codecell>

from scipy.optimize import minimize
lifeDemand = 24000
trendPerMonth = -.00
yearsLife = 2
seasonCoeffs = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]
demand = calc_demand(lifeDemand, trendPerMonth, yearsLife, seasonCoeffs)

fmc = 1000       # Fixed manufacturing cost
perOrder = 80.00 # per order cost
vmc = 2.00       # variable manufacturing cost
interest = .12   # WACC for pricing inventory carrying cost

def inv_stats(orders, demand):
    invStart = []
    invEnd = []
    invAvg = []

    for i, order in enumerate(orders):
        # calculate starting inventory
        if i == 0:
            invStart.append(0)  # eventually replace this with an optional input
        else:
            invStart.append(invEnd[i-1])
        
        # calculate ending inventory from inventory balance equation
        invEnd.append(invStart[i] - demand[i] + orders[i])

        # calculate average inventory in order to calculate period carrying cost
        invAvg.append((invStart[i]+invEnd[i])/2)

    return invStart, invEnd, invAvg

def optimize_order_cost(fmc, demand, perOrder, vmc, interest, guess, method):

    def adjusted_orders(orders):
        orders = [max(0, x) for x in orders]        
        orders = [sum(demand) - sum(orders)] + orders

        if orders[0] < 0:
            orders[0] = 0

        return orders

    def calc_order_cost_a(orders):
        # function should return total cost

        orders = adjusted_orders(orders)
        invStart, invEnd, invAvg = inv_stats(orders, demand)

        # calculate costs
        # need blended cost if there were a POD order

        ###### look into PEP 8 guidelines #####

        fixed_cost = [fmc + perOrder if order else 0 for order in orders]
        variable_cost = [vmc * order for order in orders]
        umc = (sum(fixed_cost)+sum(variable_cost)) / (sum(orders))
        carrying_cost = [float(interest) / 12 * month_avg * umc for month_avg in invAvg] 

        total_cost = sum(fixed_cost + variable_cost + carrying_cost)

        if not total_cost > -1:
            print "nan found"
            print fixed_cost
            print variable_cost
            print orders
            raise ValueError

        return total_cost

    opt =  minimize(calc_order_cost_a, guess, method = method)
    # 1: use a method with bounds; pass in bounds directly
    # 2: pass in as a guess *only* months 2 through n
    # 3: adjust constraints

    print 'Min cost: %s' %opt['fun']
    opt_sched = opt['x']
    print 'Optimal schedule: %s' %opt_sched
    ### adjust this so proper schedule is printed
    opt_sched = adjusted_orders(opt_sched)
    print 'Optimal schedule, human readable: %s' %opt_sched
    return opt['fun']

guess = [0] * len(demand)

# optimize_order_cost(fmc, demand, perOrder, vmc, interest, guess, method = 'Powell')


print "Powell, guess simple order:"
x = optimize_order_cost(fmc, demand, perOrder, vmc, interest, demand[1:], method = 'Powell')
optimize_order_cost(fmc, demand, perOrder, vmc, interest, demand[1:], method = 'Powell')

print "Powell, guess 0 orders:"
y = optimize_order_cost(fmc, demand, perOrder, vmc, interest, guess[1:], method = 'Powell')

# print "Powell, guess EOQ"
# print "Powell, order 9 months"

# <codecell>

# <codecell>

# to do:
# 1. 
# 2. update to handle POD - make sure to check if there's no POD available...handle default
#    Python idioms?
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

