document.addEventListener('DOMContentLoaded', () => {
    main();
})

var sys_prompt = [];

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function main() {
    window.onload = function () {
        const overlay = document.createElement('div');
        overlay.id = 'overlay';
        overlay.innerHTML = `
            <div id="prompt-box">
                <h2>Enter a system prompt (A Description Of the The AI.You Can Leave It Blank If You Want.):</h2>
                <textarea placeholder="Give A Detailed Description Of Instructions And Restraints For the AI To Make It Your Own." id="system-prompt-input" rows="4" cols="50"></textarea>
                <br>
                <button id="submit-prompt">Submit</button>
            </div>
        `;
        document.body.appendChild(overlay);

        document.getElementById('submit-prompt').addEventListener('click', function () {
            const promptInput = document.getElementById('system-prompt-input').value;
            if (promptInput.trim() !== "") {
                sys_prompt.push({ "role": "system", "content": promptInput });
            }
            else {
                sys_prompt.push({ "role": "system", "content": "your name is lexi.you are a helpful assistant." });
            }
            document.body.removeChild(overlay);
        });
    };

    document.getElementById('send-button').addEventListener('click', async function () {
        const sendButton = document.getElementById('send-button');
        const userInput = document.getElementById('user-input').value;
        const chatBox = document.getElementById('chat-box');
        const box = document.getElementById('box');
        const load = document.getElementById('load');
        if (userInput.trim() === "") return;

        // Create a new element for the user message
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'user-message';
        userMessageElement.textContent = userInput;
        chatBox.appendChild(userMessageElement);

        document.getElementById('user-input').value = '';

        // Set loading state
        sendButton.disabled = true;
        sendButton.style.backgroundColor = 'grey';

        // Add loading circle
        load.style.display = 'inline-block';

        const aiMessageElement = document.createElement('div');
        aiMessageElement.className = 'ai-message';
        //aiMessageElement.textContent = out;
        chatBox.appendChild(aiMessageElement);


        const out = await generateEvilResponse(userInput, aiMessageElement);
        // Create a new element for the AI message


        // Reset button state
        sendButton.disabled = false;
        sendButton.style.backgroundColor = '';

        // Remove loading circle
        load.style.display = 'none';





    });
}

function appendMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = 0; //chatBox.scrollHeight; // Auto-scroll to the bottom
}

async function generateEvilResponse(userInput, aiMessageElement) {

    const data = {
        userIn: userInput,
        sys_prompt: sys_prompt
    };

    const csrftoken = getCookie('csrftoken');

    try {
        const response = await fetch('/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let output = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            output += decoder.decode(value, { stream: true });
            aiMessageElement.textContent = output;
        }

    } catch (error) {
        console.error('Error:', error);
    }
}
