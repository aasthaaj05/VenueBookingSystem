function approveRequest(requestId) {
    fetch(`/gymkhana/approve/${requestId}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() }
    }).then(response => response.json())
    .then(data => {
        if (data.status === "approved") location.reload();
    });
}

function openDeclineModal(requestId) {
    document.getElementById('modalOverlay').style.display = 'block';
    document.getElementById('reasonModal').style.display = 'block';
    document.getElementById('reasonModal').dataset.requestId = requestId;
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
    document.getElementById('reasonModal').style.display = 'none';
}

function submitDecline() {
    const requestId = document.getElementById('reasonModal').dataset.requestId;
    const reason = document.getElementById('reasonText').value.trim();
    if (!reason) {
        alert('Please provide a reason for declining.');
        return;
    }

    fetch(`/gymkhana/decline/${requestId}/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken(), "Content-Type": "application/json" },
        body: JSON.stringify({ rejection_reason: reason })
    }).then(() => location.reload());
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
