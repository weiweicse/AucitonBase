import web

db = web.database(dbn='sqlite',
        db='auctions.db'
    )
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON') # Enable foreign key constraints
                                     # WARNING: DO NOT REMOVE THIS!

######################BEGIN HELPER METHODS######################

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except:
#     t.rollback()
#     raise
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # the correct column and table name in your database
    query_string = 'select Curr_time from Time;'
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].Curr_time
                                  # column name

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    query_string = 'select * from Item where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    if isResultEmpty(result):
        return None
    else:
        result = query(query_string, {'itemID': item_id})
        return result[0]

# helper method to determine whether query result is empty
# Sample use:
# query_result = sqlitedb.query('select currenttime from Time')
# if (sqlitedb.isResultEmpty(query_result)):
#   print 'No results found'
# else:
#   .....
#
# NOTE: this will consume the first row in the table of results,
# which means that data will no longer be available to you.
# You must re-query in order to retrieve the full table of results
def isResultEmpty(result):
    try:
        result[0]
        return False
    except:
        return True

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return db.query(query_string, vars)

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time

# updates current time in the database
def updateTime(time):
    query_string = 'update Time set Curr_time = $time;'
    result = query(query_string, {'time': time})

# find a particular auction
def getBidsByItemID(item_id, current_time):
    query_string = 'select * from Bid where ItemID = $itemID and Time <= $time;'
    results = query(query_string, {'itemID': item_id, 'time': current_time})
    return results

# get the number of bids associated with a certain item
def getNumberOfBids(item_id, current_time):
    query_string = 'select count(*) as cnt from Bid where ItemID = $itemID and Time <= $time;'
    result = query(query_string, {'itemID': item_id, 'time': current_time})
    return result[0].cnt

# get the current price of a certain auction at a certain time
def getCurrentPrice(item_id, current_time):
    query_string = 'select max(Amount) as currently from Bid where ItemID = $itemID and Time <= $time;'
    result = query(query_string, {'itemID': item_id, 'time': current_time})
    return result[0].currently

def getCategoryByItemID(item_id):
    query_string = 'select * from Category where ItemID = $itemID;'
    results = query(query_string, {'itemID': item_id})
    return results

# get the winner of a certain auction
def getWinner(item_id):
    query_string = 'select UserID from Bid B where ItemID = $itemID and not exists (select * from Bid where ItemID = $itemID and Amount > B.Amount);'
    result = query(query_string, {'itemID': item_id}).list()
    if result:
        return result[0].UserID
    else:
        return "NOBODY"

# add a new bid for a given item
def addBid(item_id, user_id, current_time, amount):
    query_string = 'insert into Bid values($itemID, $userID, $time, $amount)'
    result = query(query_string, {'itemID': item_id, 'userID': user_id, 'time': current_time, 'amount': amount})

# get auctions that satisfies cetain conditions
def getAuctionByCondition(price_low, price_high, category, open_or_not, close_or_not):
    query_string ='select * from Item where Currently >= $price_low and Currently <= $price_high'
    current_time = getTime()
    if open_or_not == 'true' and close_or_not == 'true':
        query_string += ' and started <= $time'
    elif open_or_not == 'true' and close_or_not == 'false':
        query_string += ' and started <= $time and ends >= $time'
    elif open_or_not == 'false' and close_or_not == 'true':
        query_string += ' and ends < $time'
    else:
        return []

    if category != 'All':
        query_string += ' and ItemID in (select ItemID from Category where Category = $category)'
    results = query(query_string + ' order by Number_of_Bids DESC', {'price_low': price_low, 'price_high': price_high, 'time': current_time, 'category': category})
    return results
