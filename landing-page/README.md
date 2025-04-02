# PrometheusAI Trading Bot Landing Page

A modern, responsive landing page for the PrometheusAI trading bot platform. This landing page is designed to showcase the trading bot's features, pricing, and collect early access signups.

## Features

- Clean, modern design with Pantone turquoise and light tan color scheme
- Mobile-responsive layout
- Interactive animations and UI elements
- Early access signup form with data collection
- Easy to customize and deploy

## Project Structure

```
landing-page/
├── index.html            # Main landing page
├── styles.css            # CSS styles
├── script.js             # JavaScript functionality
├── formhandler.php       # PHP script for form processing
├── thank-you.html        # Thank you page after successful signup
├── error.html            # Error page for failed signups
├── data/                 # Directory for storing signups (CSV)
│   └── signups.csv       # CSV file with signup data
└── README.md             # This documentation
```

## Setup Instructions

### 1. Prerequisites

- Web server with PHP support (for form handling)
- Basic understanding of HTML, CSS, and JavaScript

### 2. Installation

1. Upload all files to your web server
2. Ensure the `data` directory has write permissions for the web server user
3. Update configuration in `formhandler.php` with your email address

```php
// In formhandler.php:
$recipients = ['your-email@example.com']; // Replace with your email
```

### 3. Customization

#### A. Color Scheme

To change the color scheme, modify the CSS variables in `styles.css`:

```css
:root {
    --color-primary: #40E0D0; /* Pantone Turquoise */
    --color-primary-dark: #35B8AB;
    --color-primary-light: #7CEAE0;
    --color-secondary: #F5F5DC; /* Light Tan */
    --color-secondary-dark: #E8E8C8;
    /* ...other variables... */
}
```

#### B. Content

Update the content in `index.html` to match your specific offering:

- Replace the feature descriptions
- Update pricing information
- Change testimonials
- Modify FAQ questions and answers

#### C. Images

1. Add your own dashboard screenshot by replacing the reference to `trading-dashboard.png`
2. Update any other image assets as needed

#### D. Social Media

Update social media links in the footer section:

```html
<div class="social-links">
    <a href="https://twitter.com/your_handle"><i class="fab fa-twitter"></i></a>
    <a href="https://linkedin.com/in/your_profile"><i class="fab fa-linkedin-in"></i></a>
    <!-- Other social links -->
</div>
```

### 4. Form Integration

The landing page includes a PHP form handler for collecting email signups. When a user submits the form:

1. The data is validated
2. A record is saved to `data/signups.csv`
3. An email notification is sent to the specified recipients
4. The user is redirected to the thank-you page

To connect the form to your backend or CRM instead:

1. Open `script.js`
2. Modify the form submission handler to send data to your API:

```javascript
// In script.js
earlyAccessForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get form data
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        tradingExperience: document.getElementById('trading-experience').value,
        plan: document.getElementById('plan').value
    };
    
    // Send to your API or service
    fetch('https://your-api-endpoint.com/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        // Handle successful signup
        window.location.href = 'thank-you.html';
    })
    .catch(error => {
        // Handle error
        window.location.href = 'error.html';
    });
});
```

## Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Android Chrome)

## Performance Optimization

- Minify CSS and JavaScript for production
- Optimize and compress images
- Consider using a CDN for font awesome icons
- Enable browser caching through server configuration

## License

This landing page template is provided for your use with the PrometheusAI trading bot platform.

## Support

For questions or assistance, please contact support@prometheusai.com 