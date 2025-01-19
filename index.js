
const express = require('express');
const fs = require('fs');
const csv = require('csv-parser');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = 5000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

let products = [];

// Load the dataset from CSV
fs.createReadStream(path.join(__dirname, 'data', 'Air Conditioners.csv'))
    .pipe(csv())
    .on('data', (row) => {
        // Store the products in an array
        products.push(row);
    })
    .on('end', () => {
        console.log('CSV file successfully processed');
    });

// Route to serve the form
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Route to handle form submission and get recommendations
app.post('/recommend', (req, res) => {
    const { brand, category, price } = req.body;

    // Filter products based on user input
    let filteredProducts = products.filter(product => {
        const isBrandMatch = brand ? product.name.toLowerCase().includes(brand.toLowerCase()) : true;
        const isCategoryMatch = category ? product.main_category.toLowerCase() === category.toLowerCase() : true;
        const isPriceMatch = price ? parseFloat(product.discount_price.replace(/[^\d.-]/g, '')) <= parseFloat(price) : true;
        return isBrandMatch && isCategoryMatch && isPriceMatch;
    });

    if (filteredProducts.length === 0) {
        res.send('<h2>No products found matching your criteria.</h2><a href="/">← Back to Search</a>');
        return;
    }

    // Generate HTML to display products
    let html = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Recommended Products</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 50px; }
                .product { border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; }
                .product img { max-width: 200px; }
                .back-link { margin-top: 20px; display: block; }
            </style>
        </head>
        <body>
            <h1>Recommended Products</h1>
    `;

    filteredProducts.forEach(product => {
        html += `
            <div class="product">
                <h2>${product.name}</h2>
                <img src="${product.image}" alt="${product.name}">
                <p><strong>Price:</strong> ${product.discount_price} <s>${product.actual_price}</s></p>
                <p><strong>Ratings:</strong> ${product.ratings} (${product.no_of_ratings} ratings)</p>
                <p><a href="${product.link}" target="_blank">View Product</a></p>
            </div>
        `;
    });

    html += `<a href="/" class="back-link">← Back to Search</a></body></html>`;

    res.send(html);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
