#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/findauction', 'find_auction',
        '/placebid', 'place_bid',
        '/browse', 'browse_auctions',
        '/500', 'server_error',
        '/login', 'login',
        '/logout', 'logout',
        '/profile', 'profile',
        '/', 'browse_auctions',
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )

web.config.debug = False
web.internalerror = web.debugerror
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'))
app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time, username = session.get('username', None))

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html', username = session.get('username', None))

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)

        # save the selected time as the current time in the database
        sqlitedb.updateTime(selected_time)

        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message, username = session.get('username', None))

class find_auction:

    def GET(self):
        item_id = web.input(itemid=None).itemid
        if item_id is None:
            return render_template('find_auction.html', username = session.get('username', None))
        else:
            # check the status of the current auction
            current_time = sqlitedb.getTime()
            item = sqlitedb.getItemById(item_id)

            if item is None:
                return render_template('find_auction.html', status = "NOT FOUND", username = session.get('username', None))


            # calculate current price
            current_price = sqlitedb.getCurrentPrice(item_id, current_time)
            if current_price is None:
                current_price = item.First_Bid
            item.Currently = current_price

            web.debug(item.Currently)
            web.debug(item.Buy_Price)

            # check the current status of the auction
            status = getAuctionStatus(current_time, item.Started, item.Ends, item.Currently, item.Buy_Price)
            if status == "NOT FOUND":
                return render_template('find_auction.html', status = status, username = session.get('username', None))

            # modify values inside item to make it consistent with the current timestamp
            bids = sqlitedb.getBidsByItemID(item_id, current_time)
            categories = sqlitedb.getCategoryByItemID(item_id)
            if status == "OPEN":
                number_of_bids = sqlitedb.getNumberOfBids(item_id, current_time)
                
                item.Number_of_Bids = number_of_bids
                item.Currently = current_price
                return render_template('find_auction.html', item = item, categories = categories, bids = bids, status = status, username = session.get('username', None))
            else:
                winner = sqlitedb.getWinner(item_id)
                return render_template('find_auction.html', item = item, categories = categories, bids = bids, status = status, winner = winner, username = session.get('username', None))


class place_bid:

    def GET(self):
        raise web.seeother('/findauction')

    def POST(self):
        post_params = web.input()
        item_id = post_params['itemid']
        user_id = post_params['userid']
        amount = post_params['amount']
        current_time = sqlitedb.getTime()

        web.debug(item_id)
        web.debug(user_id)
        web.debug(amount)

        t = sqlitedb.transaction()
        try:
            sqlitedb.addBid(item_id, user_id, current_time, amount)
        except:
            t.rollback()
            raise web.seeother('/500?errortype={0}&errorvalue={1}'.format(sys.exc_info()[0], sys.exc_info()[1]))
        else:
            t.commit()

        return render_template('place_bid.html', itemid = item_id, username = session.get('username', None))

# category, open/close, price
class browse_auctions:

    def GET(self):
        submit = web.input(submit="false").submit
        if submit == "true":
            open_or_not = web.input(open="false").open
            close_or_not = web.input(close="false").close
            web.debug(open_or_not)
            web.debug(close_or_not)
            category = web.input(category="All").category
            price = web.input(price="0|100000").price.split('|')
            price_low = price[0]
            price_high = price[1]
            items = sqlitedb.getAuctionByCondition(price_low, price_high, category, open_or_not, close_or_not)
            return render_template('browse.html', items = items, username = session.get('username', None))
        elif submit == "false":
            return render_template('browse.html', username = session.get('username', None))

class login:
    def GET(self):
        return render_template('login.html')

    def POST(self):
        username = web.input(username=None).username
        password = web.input(password=None).password
        if auth(username, password):
            session.loggedin = True
            session.username = username
            raise web.seeother('/')
        else:
            raise web.seeother('/500')

class logout:
    def GET(self):
        session.kill()
        return render_template('logout.html')

class profile:
    def GET(self):
        if session.get('loggedin', False) == True:
            return render_template('profile.html', username = session.get('username', None))
        return web.seeother('/500')

class server_error:

    def GET(self):
        error_type = web.input(errortype=None).errortype
        error_value = web.input(errorvalue=None).errorvalue
        if error_type is None or error_value is None:
            return render_template('500.html')
        else:
            return render_template('500.html', error_type = error_type, error_value = error_value, username = session.get('username', None))

######################BEGIN HELPER METHODS######################

def getAuctionStatus(current_time, started, ends, currently, buy_price):
    if (buy_price != "" and currently >= buy_price) or current_time > ends:
        return "CLOSED"
    elif current_time > started and current_time < ends:
        return "OPEN"
    else:
        return "NOT FOUND"

def auth(username, password):
    return sqlitedb.verify(username, password)


######################END HELPER METHODS######################

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    app.run()
