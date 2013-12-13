Basic capabilities
==================

1. Manually change the current time
-----------------------------------

You can manually change the current time in
http://www.stanford.edu/~wwei2/cgi-bin/auctionbase.py/selecttime.

You can select the time you want to change and the website will do the
rest for you.

2. Auction users enter bids on open auctions
--------------------------------------------

If you know the ID of the item you want to bid, you can enter the Item
ID in url /findauction. When you are looking at an auction that is open,
 the website will display a form for users to enter bids. If the auction
 is closed, you will not be able to enter bids.

3. Automatic auction closing. 
-----------------------------

When you look up an item in url /findauction, the website will tell you
whether the auction is open or not.

4. Ability to see the winner of a closed auction.
-------------------------------------------------

When you lookup an auction in url /findauction, if the auction is
closed, the website will tell you the winner of the auction. However, it
is possible that there is no winner for the auction, then the website
will display "The winner is NOBODY".

5. Browse auctions of interest
------------------------------

Under the url /browse, you can select the price range (6 options in
total, similar to Amazon). You can also select category you are
interested in (Categories that has the most items). You can also browse
auctions that is open or closed or all.

6. Ability to find an (open or closed) auction based on itemID.
---------------------------------------------------------------

Under url
http://www.stanford.edu/~wwei2/cgi-bin/auctionbase.py/findauction, you
can find an auction based on itemID that is open or closed.

Input parameters a user can provide when browsing auctions
==========================================================

1. Price (all, 0-25, 25-50, 50-100, 100-200, 200-)
2. Category (12 options to choose from plus all)
3. Open/Close status (open, closed, or both)

A list of any capabilities in your system beyond the basic requirements
=======================================================================

1. A more beautiful interface
2. Support time travel. You can enter a bid that is bigger than the
   highest price for current time but is smaller than the smallest one
of the future bids.
3. Use JavaScript to check user input. If user enter a string but not a
   real number in price field, the website will pop out an alert.
