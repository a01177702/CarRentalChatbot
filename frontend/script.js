
const API_URL = 'http://127.0.0.1:5000/chat';

const chatInput = document.querySelector('.chat-input');
const sendIcon = document.querySelector('.send-icon');
const messagesContainer = document.querySelector('.chatbot-messages');
const bookingContainer = document.querySelector('.summary-section .inner-container'); // Booking Options Container

function createMessageElement(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', isUser ? 'user-message' : 'ai-message');
    let formattedMessage = message.replace(/([.?!])\s+/g, '$1<br><br>');
    messageDiv.innerHTML = `<p>${formattedMessage}</p>`;
    messagesContainer.prepend(messageDiv);
    messagesContainer.scrollTop = 0;
}

function addBookingCard(details) {
    const cardDiv = document.createElement('div');
    cardDiv.classList.add('card');

    cardDiv.innerHTML = `
        <h3>${details.brand} ${details.model}</h3>
        <ul>
            <li><strong>Year:</strong> ${details.year}</li>
            <li><strong>Color:</strong> ${details.color}</li>
            <li><strong>Location:</strong> ${details.location}</li>
            <li><strong>Price:</strong> $${details.price}/day</li>
        </ul>
    `;
    bookingContainer.appendChild(cardDiv);
}

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    createMessageElement(message, true);
    chatInput.value = '';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        if (data.response) {
            if (data.response.car_details) {
                // Add booking card if car details are provided
                addBookingCard(data.response.car_details);
            }
            createMessageElement(data.response.message || data.response);
        } else {
            createMessageElement("Error: Could not get response from chatbot.");
        }
    } catch (error) {
        createMessageElement("Error: Could not connect to chatbot.");
        console.error("Error:", error);
    }
}

sendIcon.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

document.addEventListener('DOMContentLoaded', setCurrentDate);
