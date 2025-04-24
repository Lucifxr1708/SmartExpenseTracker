
document.addEventListener('DOMContentLoaded', function() {
    // Set default date to today for the expense form
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.valueAsDate = new Date();
    }

    // Add automatic fade-out for flash messages
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s';
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 500);
        }, 3000);
    });
});
