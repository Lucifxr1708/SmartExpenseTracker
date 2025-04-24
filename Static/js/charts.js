document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    const canvas = ctx.canvas;

    // Get data from the page
    const categoryElements = document.querySelectorAll('#expensesByCategory p');
    const categories = [];
    const amounts = [];

    categoryElements.forEach(element => {
        const text = element.textContent;
        if (text.includes(':')) {
            const [category, amount] = text.split(':');
            if (!category.includes('Total')) {  // Skip total row
                categories.push(category.trim());
                amounts.push(parseFloat(amount.replace('$', '').trim()));
            }
        }
    });

    // Check if we have data
    if (categories.length === 0) {
        // Show "No data available" message
        canvas.style.height = '300px';  // Set fixed height
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#666';
        ctx.fillText('No expense data available for this period', canvas.width / 2, canvas.height / 2);
        return;
    }

    // Create the chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'Expenses by Category'
                }
            }
        }
    });
});