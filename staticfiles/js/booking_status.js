// document.addEventListener("DOMContentLoaded", () => {
//     populateTable();
// });

// // // Dummy Data
// // const dummyRequests = [
// //     {
// //         request_id: 'a1b2c3d4',
// //         date: '2023-12-15',
// //         time: '14:00',
// //         venue: { name: 'Mini Audi', capacity: 150 },
// //         user: { organization_name: 'Tech Club' },
// //         event_details: 'Annual Coding Competition',
// //         status: 'pending',
// //     },
// //     {
// //         request_id: 'e5f6g7h8',
// //         date: '2023-12-16',
// //         time: '10:00',
// //         venue: { name: 'AC Auditorium', capacity: 200 },
// //         user: { organization_name: 'Cultural Fest' },
// //         event_details: 'Dance Competition Finals',
// //         status: 'approved',
// //     },
// //     {
// //         request_id: 'i9j0k1l2',
// //         date: '2023-12-17',
// //         time: '16:00',
// //         venue: { name: 'Seminar Hall', capacity: 80 },
// //         user: { organization_name: 'Physics Department' },
// //         event_details: 'Guest Lecture on Quantum Physics',
// //         status: 'rejected',
// //         reasons: 'Venue under maintenance',
// //     }
// // ];

// // Initialize table
// function populateTable() {
//     const tbody = document.querySelector('#bookingsTable tbody');
//     tbody.innerHTML = '';

//         Requests.forEach(request => {
//         const row = document.createElement('tr');
//         row.innerHTML = `
//             <td>${request.date} ${request.time}</td>
//             <td>${request.venue.name} (${request.venue.capacity} seats)</td>
//             <td>${request.user.organization_name}</td>
//             <td>${request.event_details}</td>
//             <td class="status-${request.status}">${request.status.toUpperCase()}</td>
//             <td class="action-buttons">
//                 ${request.status === 'pending' ? 
//                     `<button class="btn approve-btn" onclick="approveRequest('${request.request_id}')">Approve</button>
//                     <button class="btn decline-btn" onclick="openDeclineModal('${request.request_id}')">Decline</button>` : 
//                     request.reasons ? `<strong>Reason:</strong> ${request.reasons}` : ''}
//             </td>
//         `;
//         tbody.appendChild(row);
//     });
// }

// // Action functions
// let currentRequestId = null;

// function approveRequest(requestId) {
//     const request = dummyRequests.find(r => r.request_id === requestId);
//     request.status = 'approved';
//     populateTable();
// }

// function openDeclineModal(requestId) {
//     currentRequestId = requestId;
//     document.getElementById('modalOverlay').style.display = 'block';
//     document.getElementById('reasonModal').style.display = 'block';
// }

// function closeModal() {
//     document.getElementById('modalOverlay').style.display = 'none';
//     document.getElementById('reasonModal').style.display = 'none';
//     currentRequestId = null;
//     document.getElementById('reasonText').value = '';
// }

// function submitDecline() {
//     const reason = document.getElementById('reasonText').value;
//     const request = dummyRequests.find(r => r.request_id === currentRequestId);
//     request.status = 'rejected';
//     request.reasons = reason;
//     populateTable();
//     closeModal();
// }



document.addEventListener("DOMContentLoaded", () => {
    // Fetch the requests data from the template variable injected by Django
    const requests = JSON.parse(document.getElementById("requestsData").textContent);
    populateTable(requests);
});

// Function to populate the table with booking requests
function populateTable(requests) {
    const tbody = document.querySelector('#bookingsTable tbody');
    tbody.innerHTML = '';  // Clear existing content

    requests.forEach(request => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${request.date} ${request.time}</td>
            <td>${request.venue.name} (${request.venue.capacity} seats)</td>
            <td>${request.user.organization_name}</td>
            <td>${request.event_details}</td>
            <td class="status-${request.status}">${request.status.toUpperCase()}</td>
            <td class="action-buttons">
                ${request.status === 'pending' ? 
                    `<button class="btn approve-btn" onclick="approveRequest('${request.request_id}')">Approve</button>
                    <button class="btn decline-btn" onclick="openDeclineModal('${request.request_id}')">Decline</button>` : 
                    request.reasons ? `<strong>Reason:</strong> ${request.reasons}` : ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Action functions
let currentRequestId = null;

// Function to approve a request
function approveRequest(requestId) {
    const request = requests.find(r => r.request_id === requestId);
    request.status = 'approved';
    populateTable(requests);  // Refresh the table
}

// Function to open the decline modal
function openDeclineModal(requestId) {
    currentRequestId = requestId;
    document.getElementById('modalOverlay').style.display = 'block';
    document.getElementById('reasonModal').style.display = 'block';
}

// Function to close the modal
function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
    document.getElementById('reasonModal').style.display = 'none';
    currentRequestId = null;
    document.getElementById('reasonText').value = '';
}

// Function to submit a decline reason
function submitDecline() {
    const reason = document.getElementById('reasonText').value;
    if (!reason) {
        alert("Please provide a reason for declining the request.");
        return;
    }

    const request = requests.find(r => r.request_id === currentRequestId);
    request.status = 'rejected';
    request.reasons = reason;

    populateTable(requests);  // Refresh the table
    closeModal();
}


document.addEventListener("DOMContentLoaded", () => {
    const requests = JSON.parse(document.getElementById("requestsData").textContent);
    populateTable(requests);
});

function populateTable(requests) {
    const tbody = document.querySelector('#bookingsTable tbody');
    tbody.innerHTML = '';

    requests.forEach(request => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${request.date} ${request.time}</td>
            <td>${request.venue.name} (${request.venue.capacity} seats)</td>
            <td>${request.user.organization_name}</td>
            <td>${request.event_details}</td>
            <td class="status-${request.status}">${request.status.toUpperCase()}</td>
            <td class="action-buttons">
                ${request.status === 'pending' ? 
                    `<button class="btn approve-btn" onclick="approveRequest('${request.request_id}')">Approve</button>
                    <button class="btn decline-btn" onclick="openDeclineModal('${request.request_id}')">Decline</button>` : 
                    request.reasons ? `<strong>Reason:</strong> ${request.reasons}` : ''}
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Approve Request
function approveRequest(requestId) {
    fetch(`/gymkhana/approve/${requestId}/`, { method: "POST", headers: { "X-CSRFToken": getCSRFToken() } })
        .then(response => response.json())
        .then(data => {
            if (data.status === "approved") location.reload();
        });
}

// Decline Request (Opens Modal)
function openDeclineModal(requestId) {
    document.getElementById("declineRequestId").value = requestId;
    document.getElementById("declineModal").style.display = "block";
}

// Close Modal
function closeDeclineModal() {
    document.getElementById("declineModal").style.display = "none";
}

// Submit Decline
document.getElementById("declineForm").onsubmit = function(event) {
    event.preventDefault();
    const requestId = document.getElementById("declineRequestId").value;
    const reason = document.getElementById("rejectionReason").value;

    fetch(`/gymkhana/decline/${requestId}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken(), "Content-Type": "application/x-www-form-urlencoded" },
        body: `rejection_reason=${encodeURIComponent(reason)}`
    }).then(() => location.reload());
};

// Get CSRF Token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}


