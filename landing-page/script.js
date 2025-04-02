document.addEventListener('DOMContentLoaded', function() {
    // Form submission handling
    const earlyAccessForm = document.getElementById('early-access-form');
    if (earlyAccessForm) {
        earlyAccessForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                tradingExperience: document.getElementById('trading-experience').value,
                plan: document.getElementById('plan').value
            };
            
            // Simple form validation
            if (!formData.name || !formData.email || !formData.tradingExperience || !formData.plan) {
                alert('Please fill in all fields');
                return;
            }
            
            // Here you would typically send the data to your server
            // For now, we'll just simulate a successful submission
            earlyAccessForm.innerHTML = '<div class="success-message"><h3>Thank you for your interest!</h3><p>We\'ll be in touch soon with your early access details.</p></div>';
            
            // Log the data (for demonstration purposes)
            console.log('Form submitted with data:', formData);
        });
    }
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Mobile menu toggle (placeholder - would need to be expanded for a real mobile menu)
    const setupMobileMenu = () => {
        // This is a placeholder for mobile menu functionality
        // In a real implementation, you would add the necessary HTML and CSS
        console.log('Mobile menu functionality would be implemented here');
    };
    
    // Simple animation on scroll
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.feature-card, .pricing-card, .step, .faq-item');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        elements.forEach(element => {
            observer.observe(element);
        });
    };
    
    // Add CSS for the animation
    const addAnimationStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            .feature-card, .pricing-card, .step, .faq-item {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.5s ease, transform 0.5s ease;
            }
            
            .feature-card.animate, .pricing-card.animate, .step.animate, .faq-item.animate {
                opacity: 1;
                transform: translateY(0);
            }
        `;
        document.head.appendChild(style);
    };
    
    // Initialize animations
    addAnimationStyles();
    animateOnScroll();
    
    // Initialize other functions
    setupMobileMenu();
    
    // Display a message in the console
    console.log('PrometheusAI Landing Page Initialized');
}); 