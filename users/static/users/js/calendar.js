document.addEventListener('DOMContentLoaded', () => {
    // Calendar elements
    const calendarDays = document.getElementById('calendarDays');
    const currentMonthElement = document.getElementById('currentMonth');
    const prevMonthButton = document.getElementById('prevMonth');
    const nextMonthButton = document.getElementById('nextMonth');
    const resetSelectionButton = document.getElementById('resetSelection');
    const confirmDateButton = document.getElementById('confirmDate');
    const selectedDateDisplay = document.getElementById('selectedDateDisplay');
    const selectedDateText = document.getElementById('selectedDateText');
    const bookingInfo = document.getElementById('bookingInfo');
    const bookingDateElement = document.getElementById('bookingDate');
    const startTime = document.getElementById('startTime');
    const backToCalendarButton = document.getElementById('backToCalendar');
    const confirmBookingButton = document.getElementById('confirmBooking');
    const notification = document.getElementById('notification');

    // Current date and selected date
    const today = new Date();
    let currentMonth = today.getMonth();
    let currentYear = today.getFullYear();
    let selectedDate = null;
    let selectedTimeSlot = null;

    // Example of unavailable dates (in a real app, these would come from your backend)
    const unavailableDates = [
        new Date(2025, 1, 10).toDateString(),
        new Date(2025, 1, 15).toDateString(),
        new Date(2025, 1, 20).toDateString()
    ];

    // Example of dates with events (in a real app, these would come from your backend)
    const eventsOnDates = [
        new Date(2025, 1, 5).toDateString(),
        new Date(2025, 1, 12).toDateString(),
        new Date(2025, 1, 25).toDateString()
    ];

    // Generate month name
    function getMonthName(month) {
        const months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        return months[month];
    }

    // Generate the calendar
    function generateCalendar(month, year) {
        calendarDays.innerHTML = '';

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startDayOfWeek = firstDay.getDay();

        // Update the month and year display
        currentMonthElement.textContent = `${getMonthName(month)} ${year}`;

        // Add empty cells for days before the first day of the month
        for (let i = 0; i < startDayOfWeek; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.classList.add('calendar-day', 'disabled');
            calendarDays.appendChild(emptyDay);
        }

        // Add days of the current month
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.classList.add('calendar-day');
            dayElement.textContent = day;

            const currentDate = new Date(year, month, day);

            // Check if this day is today
            if (currentDate.toDateString() === today.toDateString()) {
                dayElement.classList.add('today');
            }

            // Check if this day is the selected date
            if (selectedDate && currentDate.toDateString() === selectedDate.toDateString()) {
                dayElement.classList.add('selected');
            }

            // Check if this day is unavailable
            if (unavailableDates.includes(currentDate.toDateString()) || currentDate < today) {
                dayElement.classList.add('disabled');
            } else {
                // Add click event only for available dates
                dayElement.addEventListener('click', () => selectDate(currentDate));
            }

            // Add event indicator if there's an event on this date
            if (eventsOnDates.includes(currentDate.toDateString())) {
                const eventDot = document.createElement('div');
                eventDot.classList.add('event-dot');
                dayElement.appendChild(eventDot);
            }

            calendarDays.appendChild(dayElement);
        }
    }

    // Select a date
    function selectDate(date) {
        // Remove selected class from previously selected date
        const previouslySelected = document.querySelector('.calendar-day.selected');
        if (previouslySelected) {
            previouslySelected.classList.remove('selected');
        }

        // Find the day element for the new selected date and add selected class
        const dayElements = document.querySelectorAll('.calendar-day:not(.disabled)');
        for (const element of dayElements) {
            const day = parseInt(element.textContent);
            if (day === date.getDate()) {
                element.classList.add('selected');
                break;
            }
        }

        selectedDate = date;

        // Update selected date display
        selectedDateDisplay.style.display = 'block';
        selectedDateText.textContent = selectedDate.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    // Reset selection
    function resetSelection() {
        const selectedElement = document.querySelector('.calendar-day.selected');
        if (selectedElement) {
            selectedElement.classList.remove('selected');
        }

        selectedDate = null;
        selectedDateDisplay.style.display = 'none';
        selectedDateText.textContent = 'None selected';
    }

    // Show booking time slots
    function showBookingstartTime() {
        if (!selectedDate) {
            showNotification('Please select a date first', 'error');
            return;
        }

        bookingDateElement.textContent = selectedDate.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        // Generate time slots (in a real app, available slots would come from your backend)
        startTime.innerHTML = '';
        const startHour = 9; // 9 AM
        const endHour = 21; // 9 PM
        const interval = 1; // 1 hour intervals

        // Example of unavailable time slots (in a real app, these would come from your backend)
        const unavailablestartTime = ['12:00', '13:00', '17:00'];

        for (let hour = startHour; hour < endHour; hour += interval) {
            const timeSlotElement = document.createElement('div');
            timeSlotElement.classList.add('time-slot');

            const formattedHour = hour % 12 === 0 ? 12 : hour % 12;
            const amPm = hour < 12 ? 'AM' : 'PM';
            const timeString = `${formattedHour}:00 ${amPm}`;

            timeSlotElement.textContent = timeString;

            // Check if this time slot is unavailable
            const militaryFormat = `${hour}:00`;
            if (unavailablestartTime.includes(militaryFormat)) {
                timeSlotElement.classList.add('unavailable');
            } else {
                // Add click event for available time slots
                timeSlotElement.addEventListener('click', () => selectTimeSlot(timeSlotElement, timeString));
            }

            startTime.appendChild(timeSlotElement);
        }

        // Show booking info section
        bookingInfo.style.display = 'block';

        // Scroll to booking info section
        bookingInfo.scrollIntoView({ behavior: 'smooth' });
    }

    // Select a time slot
    function selectTimeSlot(element, timeString) {
        // Remove selected class from previously selected time slot
        const previouslySelected = document.querySelector('.time-slot.selected');
        if (previouslySelected) {
            previouslySelected.classList.remove('selected');
        }

        // Add selected class to the new selected time slot
        element.classList.add('selected');
        selectedTimeSlot = timeString;
    }

    // Confirm booking
    function confirmBooking() {
        if (!selectedDate) {
            showNotification('Please select a date', 'error');
            return;
        }

        if (!selectedTimeSlot) {
            showNotification('Please select a time slot', 'error');
            return;
        }

        // Format the date for sending to backend
        const formattedDate = `${selectedDate.getFullYear()}-${String(selectedDate.getMonth() + 1).padStart(2, '0')}-${String(selectedDate.getDate()).padStart(2, '0')}`;

        // In a real application, you would send this data to your Flask/Django backend
        // For this example, we'll simulate a backend request
        const bookingData = {
            date: formattedDate,
            time: selectedTimeSlot
        };

        // Simulate sending data to backend
        simulateBackendRequest(bookingData);
    }

    // Simulate backend request (in a real app, this would be an actual fetch or AJAX request)
    function simulateBackendRequest(data) {
        console.log('1111111111111111111111')
        console.log('Sending booking data to backend:', data);

        fetch('/users/submi1111111t_booking', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(result => {
                if (result) {  // Only process if we got JSON
                    showNotification(result.message, 'success');
                    console.log("Booking response:", result);
                    resetForm();
                }
            })
            .catch(error => {
                console.error("Error submitting booking:", error);
                showNotification('Error processing booking', 'error');
            });
            console.log('4444444444444444')
    }

    // Reset the entire form
    function resetForm() {
        resetSelection();
        selectedTimeSlot = null;
        bookingInfo.style.display = 'none';

        // Remove selected class from time slots
        const selectedTimeSlotElement = document.querySelector('.time-slot.selected');
        if (selectedTimeSlotElement) {
            selectedTimeSlotElement.classList.remove('selected');
        }
    }

    // Show notification
    function showNotification(message, type) {
        notification.textContent = message;
        notification.className = 'notification';

        if (type === 'error') {
            notification.style.backgroundColor = '#dc3545';
        } else if (type === 'success') {
            notification.style.backgroundColor = '#28a745';
        } else {
            notification.style.backgroundColor = '#4a6fa5';
        }

        notification.classList.add('show');

        // Hide notification after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    // Event listeners
    prevMonthButton.addEventListener('click', () => {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        generateCalendar(currentMonth, currentYear);
    });

    nextMonthButton.addEventListener('click', () => {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        generateCalendar(currentMonth, currentYear);
    });

    resetSelectionButton.addEventListener('click', resetSelection);
    confirmDateButton.addEventListener('click', showBookingstartTime);
    backToCalendarButton.addEventListener('click', () => {
        bookingInfo.style.display = 'none';
    });
    confirmBookingButton.addEventListener('click', confirmBooking);

    // Initialize the calendar
    generateCalendar(currentMonth, currentYear);
});


// Function to get CSRF token from the Django template
function getCSRFToken() {
    let csrfToken = null;
    const cookies = document.cookie.split('; ');

    cookies.forEach(cookie => {
        const [name, value] = cookie.split('=');
        if (name === 'csrftoken') {
            csrfToken = value;
        }
    });

    return csrfToken;
}
