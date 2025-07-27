#this info is genric, update it accorinng to app type
pageseo = {
    # Core SEO Tags
    "title": "Image Grid App - Arrange & Download Images for Reports | Bavaal.com",
    "meta_description": "Effortlessly arrange multiple images into a customizable grid and download them in Word format for professional reports and documents with Bavaal's Image Grid app.",
    "robots": "index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large",

    
    # Open Graph (Social Media)
    "og_title": "Image Grid App by Bavaal - Create Image Grids for Reports",
    "og_description": "Upload, arrange, and download image grids in Word format for your reports. Try Bavaal's Image Grid app today!",
    "og_url": "https://bavaal.com/apps/image-grid",
    "og_image": "https://bavaal.com/media/images/Bavaal-Image-Grid-app.original.png",
    "og_image_type": "image/png",
    "og_type": "website", # Changed to website as it's an application page
    "og_site_name": "Bavaal - Online Image Tools", # More specific to Bavaal's offerings
    
    # Twitter Card
    "twitter_card": "summary_large_image",
    "twitter_title": "Image Grid App: Arrange Photos for Word Reports | Bavaal",
    "twitter_description": "Quickly create and download image grids for your documents with Bavaal's Image Grid app.",
    "twitter_image": "https://bavaal.com/media/images/Bavaal-Image-Grid-app.original.png", # Same as OG image
    #"twitter_site": "@BavaalOfficial", # If Bavaal has a Twitter handle
    #"twitter_creator": "@BavaalOfficial", # If the creator is the same as the site
    
    # Technical SEO
    "canonical_url": "https://bavaal.com/apps/image-grid", # Canonical URL for the app page

    
    # Additional Meta
    "author": "Bavaal Team", # More appropriate for a company product
    "keywords": "image grid, arrange images with Captions photo grid, word document, image layout, report images, online image tool, bavaal, image editor, image conversion",
    "google_site_verification": "your_verification_code_here", # Keep this as a placeholder for your actual code
    "apple_mobile_web_app_capable": "yes", # If it's a PWA or has app-like features
    "apple_mobile_web_app_status_bar_style": "black", # For iOS Safari status bar
    "format_detection": "telephone=no", # Prevents iOS from detecting phone numbers

    # Structured Data (Schema Markup)
    "schema": {
        "context": "https://schema.org", # Use @context and @type for JSON-LD
        "type": "WebApplication", # More specific for a web application
        "name": "Image Grid App by Bavaal",
        "url": "https://bavaal.com/apps/image-grid",
        "description": "An online tool to arrange multiple images into a grid layout and download them in Microsoft Word format for reports and presentations. Image Grid with Captions",
        "applicationCategory": "Multimedia", # or "Office" or "Utilities"
        "operatingSystem": "Web",
        "browserRequirements": "Requires JavaScript. Works with Chrome, Firefox, Safari, Edge.",
        "screenshot": "https://bavaal.com/media/images/Bavaal-Image-Grid-app.original.png", # A screenshot of the app in action
        "aggregateRating": { # If you have user ratings
            "type": "AggregateRating",
            "ratingValue": "4.8",
            "reviewCount": "120"
        },
        "offers": { # If there's a free version or specific offering
            "type": "Offer",
            "price": "0", # Free to use
            "priceCurrency": "USD"
        },
        "publisher": {
            "type": "Organization",
            "name": "Bavaal",
            "url": "https://bavaal.com"
        }
    }
}