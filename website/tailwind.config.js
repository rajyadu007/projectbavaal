    /** @type {import('tailwindcss').Config} */
    module.exports = {
      content: [
        './**/templates/**/*.html', // Adjust this path to match your Django templates location
      ],
      theme: {
        extend: {
          colors: {
            primary: '#609e75',       // Updated primary color
            'primary-light': '#e6f0ec', // New color from portfolio.html
            secondary: '#3A0CA3',     // Keep if used elsewhere, otherwise can remove
            dark: '#333',             // Updated dark color
            light: '#f1f7f4',         // Updated light color
            text: '#333',             // Updated text color
            'text-light': '#555',     // Updated text-light color
            white: '#ffffff',         // New color from portfolio.html
            highlight: '#4a8d63',     // New color from portfolio.html
          },
          fontFamily: {
            sans: ['Poppins', 'sans-serif'], // Updated font family
          },
          borderWidth: {
            '3': '3px',
            '5': '5px', // Added for influencer-image border
          },
          spacing: {
            '15': '60px', // Keep if used elsewhere, otherwise can remove
            '52': '208px', // For w-52/h-52 (close to 200px)
          },
        },
      },
      plugins: [
        require('@tailwindcss/typography'),
      ],
    }
    