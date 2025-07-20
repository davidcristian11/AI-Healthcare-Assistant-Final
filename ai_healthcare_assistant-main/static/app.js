const state = {
    currentImageFile: null,
    isProcessing: false,
    conversation: []
};

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.querySelector('.chat-form');
    const chatInput = document.querySelector('.chat-input');
    const sendButton = document.querySelector('.send-btn');

    setTimeout(() => {
        showMessageWithTyping('Hello! I\'m your healthcare assistant. How can I help you today?', 'assistant');
    }, 500);

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = chatInput.value.trim();

        if (message !== '' && !state.isProcessing) {
            sendMessage(message);
        }
    });

    setupImageUpload();

    chatInput.addEventListener('input', function() {
        sendButton.disabled = chatInput.value.trim() === '';
    });

    sendButton.disabled = true;
});

function setupImageUpload() {
    const chatInputContainer = document.querySelector('.chat-input-container');
    const chatInput = document.querySelector('.chat-input');

    const imageUploadButton = document.createElement('button');
    imageUploadButton.className = 'image-upload-btn';
    imageUploadButton.type = 'button'; // Prevent form submission
    imageUploadButton.innerHTML = '<i class="fas fa-image"></i>';
    imageUploadButton.title = 'Upload medical images (MRI, X-ray, CT scan)';

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/png, image/jpeg, image/jpg';
    fileInput.style.display = 'none';
    fileInput.id = 'image-upload';

    chatInputContainer.insertBefore(imageUploadButton, chatInput);
    chatInputContainer.appendChild(fileInput);

    imageUploadButton.addEventListener('click', function() {
        if (!state.isProcessing) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            uploadImage(file);
        }
    });
}

function showMessageWithTyping(message, sender) {
    const typingElement = showMessage('', sender, true);

    const typeMessage = (text, element, speed = 10) => {
        let i = 0;
        element.textContent = '';

        element.classList.remove('loading');
        element.innerHTML = '';

        const typeNextChar = () => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeNextChar, speed);
            }
        };

        typeNextChar();
    };

    setTimeout(() => {
        typeMessage(message, typingElement);
    }, 500);

    return typingElement;
}

function showMessage(message, sender, isLoading = false) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(sender);

    if (isLoading) {
        messageElement.classList.add('loading');
        messageElement.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    } else {
        messageElement.textContent = message;
    }

    document.querySelector('.messages').appendChild(messageElement);
    scrollToBottom();

    if (!isLoading) {
        state.conversation.push({
            role: sender,
            content: message
        });
    }

    return messageElement;
}

function scrollToBottom() {
    const messagesContainer = document.querySelector('.messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function sendMessage(message) {
    if (state.isProcessing) return;

    state.isProcessing = true;

    if (state.currentImageFile) {
        sendImageAnalysisRequest("Please analyze this medical image.");
    } else {
        sendTextRequest(message);
    }
}

function sendTextRequest(message) {
    showMessage(message, 'user');

    document.querySelector('.chat-input').value = '';
    document.querySelector('.send-btn').disabled = true;

    const loadingElement = showMessage('', 'assistant', true);

    const conversationHistory = getConversationHistory();

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            conversation: conversationHistory
        })
    })
    .then(handleResponse)
    .then(data => {
        loadingElement.remove();

        if (data.error) {
            showMessage(`Error: ${data.error}`, 'assistant');
        } else {
            showMessageWithTyping(data.response, 'assistant');
        }

        state.isProcessing = false;
    })
    .catch(error => {
        loadingElement.remove();
        showMessage(`An error occurred. Please try again later.`, 'assistant');
        console.error('Error:', error);
        state.isProcessing = false;
    });
}

function uploadImage(file) {
    state.isProcessing = true;

    const formData = new FormData();
    formData.append('image', file);

    const loadingElement = showMessage('', 'assistant', true);
    loadingElement.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div> Uploading image...';

    fetch('/upload-image', {
        method: 'POST',
        body: formData
    })
    .then(handleResponse)
    .then(data => {
        if (data.success) {
            loadingElement.remove();
            state.currentImageFile = data.filename;

            sendImageAnalysisRequest("Please analyze this medical image.");

            showImagePreview(URL.createObjectURL(file));
        } else {
            loadingElement.remove();
            showMessage(`Upload failed: ${data.error}`, 'assistant');
        }

        state.isProcessing = false;
    })
    .catch(error => {
        loadingElement.remove();
        showMessage(`Error uploading image. Please try again.`, 'assistant');
        console.error('Error:', error);
        state.isProcessing = false;
    });
}

function sendImageAnalysisRequest(message) {
    showMessage(message, 'user');

    document.querySelector('.chat-input').value = '';
    document.querySelector('.send-btn').disabled = true;

    const loadingElement = showMessage('', 'assistant', true);
    loadingElement.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div> Analyzing image...';

    const conversationHistory = getConversationHistory();

    fetch('/analyze-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            filename: state.currentImageFile,
            question: message,
            conversation: conversationHistory
        })
    })
    .then(handleResponse)
    .then(data => {
        loadingElement.remove();

        if (data.error) {
            showMessage(`Analysis failed: ${data.error}`, 'assistant');
        } else {
            showMessageWithTyping(data.response, 'assistant');
        }

        state.currentImageFile = null;
        state.isProcessing = false;
    })
    .catch(error => {
        loadingElement.remove();
        showMessage(`Error analyzing image. Please try again.`, 'assistant');
        console.error('Error:', error);
        state.currentImageFile = null;
        state.isProcessing = false;
    });
}

function handleResponse(response) {
    if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
    }
    return response.json();
}

function showImagePreview(imageUrl) {
    const messageContainer = document.createElement('div');
    messageContainer.className = 'message user';

    const imgElement = document.createElement('img');
    imgElement.src = imageUrl;
    imgElement.className = 'chat-image-preview';
    imgElement.alt = 'Uploaded medical image';
    imgElement.loading = 'lazy';

    imgElement.addEventListener('click', () => {
        const lightbox = document.createElement('div');
        lightbox.className = 'dialog-overlay';
        lightbox.onclick = () => document.body.removeChild(lightbox);

        const lightboxImg = document.createElement('img');
        lightboxImg.src = imageUrl;
        lightboxImg.style.maxHeight = '90vh';
        lightboxImg.style.maxWidth = '90vw';
        lightboxImg.style.borderRadius = '8px';
        lightboxImg.style.cursor = 'zoom-out';

        lightbox.appendChild(lightboxImg);
        document.body.appendChild(lightbox);
    });

    messageContainer.appendChild(imgElement);
    document.querySelector('.messages').appendChild(messageContainer);
    scrollToBottom();

    state.conversation.push({
        role: 'user',
        content: '[Image]'
    });
}

function getConversationHistory() {
    return [...state.conversation];
}
