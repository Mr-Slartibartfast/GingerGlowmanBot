I created this project in an attempt to track down some coveted needoh squishees - a gingerbread man in particular. Target has limits to what kind of scrapers they allow to scrape their website
so in an effort to not get IP banned I decided to go with the approved scraper API. 

There are a number of different approaches in the project - email alerts, SMS (didn't work for my carrier since ATT removed email to SMS in 2025), twilio (didn't feel like paying for an account for this, 
and they don't allow custom alerts without an account), discord webhook, and a desktop widget (my personal favorite - still uses the scraper API, and python - builds a little desktop widget that 
was able to check the stock status of the item on demand). 

Pre-requisites: python libraries, and most importantly a free account to the scraper API - which was one of the approved scraper services that target allows. 

This project is not limited to needohs, and could be updated to a separate link without much effort - but the concentration was on items listen in Target's online store, but were available in the store. 
