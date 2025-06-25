let prompt = document.querySelector("#prompt");
let chatContainer = document.querySelector(".chat-container");
let audioButton = document.querySelector("#audio");  
let audioinput = document.querySelector("#audio input");

const localAPI = "https://39af-34-172-231-197.ngrok-free.app/predict";
const transcribeAPI = "https://39af-34-172-231-197.ngrok-free.app/transcribe";

let user = {
    data: null,
};

let submitButton = document.querySelector("#submit");

submitButton.addEventListener("click", () => {
    if (prompt.value.trim() !== "") {
        handlechatResponse(prompt.value);
    }
});

async function generateResponse(aiChatBox) {
    let text = aiChatBox.querySelector(".ai-chat-area");

    let requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: user.data })
    };

    try {
        let response = await fetch(localAPI, requestOptions);
        let data = await response.json();
        let apiResponse = data.response.trim();

        text.innerHTML = apiResponse;
    } catch (error) {
        console.error(error);
        text.innerHTML = "An error occurred. Please try again.";
    } finally {
        chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });
    }
}

function createChatBox(html, classes) {
    let div = document.createElement("div");
    div.innerHTML = html;
    div.classList.add(classes);
    return div;
}

function handlechatResponse(message, audioURL = null) {
    user.data = message;

    let audioHTML = audioURL
        ? `<br><audio controls src="${audioURL}" style="margin-top: 5px;"></audio>`
        : "";

    let html = `<img src="user.png" alt="" id="userImage" width="50">
                <div class="user-chat-area">
                    ${user.data}${audioHTML}
                </div>`;
    prompt.value = "";

    let userChatBox = createChatBox(html, "user-chat-box");
    chatContainer.appendChild(userChatBox);
    chatContainer.scrollTo({ top: chatContainer.scrollHeight, behavior: 'smooth' });

    setTimeout(() => {
        let html = `<img src="uniVersee.png" alt="" id="aiImage" width="50">
                    <div class="ai-chat-area">
                        <p>Loading...</p>
                    </div>`;
        let aiChatBox = createChatBox(html, "ai-chat-box");
        chatContainer.appendChild(aiChatBox);
        generateResponse(aiChatBox);
    }, 600);
}

prompt.addEventListener("keydown", (e) => {
    if (e.key == "Enter") {
        console.log(prompt.value);
        handlechatResponse(prompt.value);
    }
});

let mediaRecorder;
let audioChunks = [];

audioButton.addEventListener("click", async () => {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            const formData = new FormData();
            formData.append("file", audioBlob, "speech.wav");

            try {
                const response = await fetch(transcribeAPI, {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();
                console.log("Transcribed:", data.transcription);

                const audioURL = URL.createObjectURL(audioBlob);

                if (data.transcription) {
                    handlechatResponse(data.transcription, audioURL);
                } else {
                    handlechatResponse("Sorry, could not transcribe your audio.", audioURL);
                }
            } catch (err) {
                console.error("Transcription error:", err);
                handlechatResponse("An error occurred while transcribing.", null);
            }

            audioChunks = [];
        };

        mediaRecorder.start();
        console.log("Recording...");
        audioButton.innerHTML = "🛑 Stop";

    } else {
        mediaRecorder.stop();
        console.log("Stopped");
        audioButton.innerHTML = `<span class="material-symbols-rounded">mic</span>`;
    }
});

// Optional: remove if unused
if (typeof filebtn !== 'undefined') {
    filebtn.addEventListener("click", () => {
        filebtn.querySelector("input").click();
    });
}
document.querySelector("#download").addEventListener("click", () => {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const chatBoxes = document.querySelectorAll(".user-chat-box, .ai-chat-box");
    let y = 10;

    chatBoxes.forEach(box => {
        const isUser = box.classList.contains("user-chat-box");
        const text = box.querySelector(".user-chat-area, .ai-chat-area").textContent.trim();
        const prefix = isUser ? "You: " : "UniVerse: ";
        const lines = doc.splitTextToSize(prefix + text, 180);
        doc.text(lines, 10, y);
        y += lines.length * 10 + 10;

        if (y > 270) {
            doc.addPage();
            y = 10;
        }
    });

    doc.save("chat_log.pdf");
});
