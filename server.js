const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors()); // Allows your webpage to fetch from this server

const SCRAPER_API_KEY = ''; // scraper key here
const TARGET_URL = 'https://www.target.com/p/needoh-ginger-glowman/-/A-XXXXXXXX';

app.get('/api/check-stock', async (req, res) => {
    try {
        const response = await axios.get('https://api.scraperapi.com/', {
            params: {
                api_key: SCRAPER_API_KEY,
                url: TARGET_URL,
                render: 'true',
                country: 'us'
            },
            timeout: 70000
        });

        const html = response.data.toLowerCase();
        const outOfStockKeywords = ['out of stock', 'sold out', 'currently unavailable'];
        const isOutOfStock = outOfStockKeywords.some(keyword => html.includes(keyword));

        res.json({ inStock: !isOutOfStock, timestamp: new Date() });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch inventory status' });
    }
});

app.listen(3000, () => console.log('Backend proxy listening on port 3000'));