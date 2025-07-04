const chatui = document.getElementById('chatui');
let recognition;
let finalTranscript = '';
let output;
let isStopped = false;

function startListening() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert('does not support speech recognition.');
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    

    recognition.onstart = function() {
        window.speechSynthesis.cancel();
        output = document.createElement('p');
        output.className = 'user';
        chatui.appendChild(output);
        output.innerHTML = 'Listening...';
        chatui.scrollTop = chatui.scrollHeight;
    };

    recognition.onresult = async function(event) {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const result = event.results[i];
            if (result.isFinal) {
                finalTranscript += result[0].transcript + ' ';
            } else {
                interimTranscript += result[0].transcript;
            }
        }

        output.innerHTML = finalTranscript + '<i style="color: gray;">' + interimTranscript + '</i>';
    };

    recognition.onerror = function(event) {
        console.error('Error occurred in recognition:', event.error);
    };

    recognition.onend = function() {
        console.log('Speech recognition ended');

        if (isStopped) {
            console.log("Recognition stopped by user, not restarting.");
            return; // Prevent restart if manually stopped
        }

        if (finalTranscript.length !== 0) {
            videoPlay(finalTranscript.trim());
        } else {
            output.remove();
            setTimeout(() => {
                if (recognition) {
                    recognition.start();
                    console.log("Restarted speech recognition.");
                }
            }, 1000);
        }

        finalTranscript = '';
    };

    isStopped = false; // Reset stop flag when starting
    recognition.start();
}

async function fetchResponse(text) {
    console.log("Fetching response for:", text);
    try {
        let response = await fetch('http://localhost:5000/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'query': text})
        });

        let data = await response.json();
        console.log(data)
        return data['answer'] || "I don't have a response for that.";
    } catch (error) {
        console.error("Error fetching response:", error);
        return "I couldn't retrieve a response.";
    }
}

async function videoPlay(text) {
    let video = document.getElementById("videoPlayer");

    let output = await fetchResponse(text);
    console.log("Response received:", output);

    if (!output.trim()) {
        console.log("Empty response, not playing video.");
        return;
    }

    output = output.replace(/\*/g, ""); 
    let x = document.createElement('p');
    x.className = 'agent';
    x.innerText = output;
    container = document.getElementById('chatui')
    container.appendChild(x);
    container.scrollTop = container.scrollHeight;


    let speech = new SpeechSynthesisUtterance(output.replace(/[^\w\s.,]/g, ''));
    speech.rate = 1; // Normal speed
    speech.volume = 1; // Full volume
    speech.pitch = 1; 

    window.speechSynthesis.cancel();

    // Ensure a voice is selected
    let voices = window.speechSynthesis.getVoices();
    speech.voice = voices.find(v => v.lang === 'en-US') || voices[0];

    speech.onstart = () => {
        document.getElementById("videoPlayer").setAttribute("src", "static/videos/exp2.mp4");
        console.log("Speech started, playing video...");
        document.getElementById("videoPlayer").play();
    };

    speech.onend = () => {
        console.log("Speech ended, pausing video...");
        document.getElementById("videoPlayer").pause();
        document.getElementById("videoPlayer").setAttribute("src", "static/videos/std2.mp4");
        document.getElementById("videoPlayer").play();

        setTimeout(() => {
            if (recognition && !isStopped) {
                recognition.start();
                console.log("Restarted speech recognition.");
            }
        }, 1000);
    };

    speech.onpause = () => {
        setTimeout(() => {
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.resume();
                console.log("Resumed speech synthesis.");
            }
        }, 100);
    };

    window.speechSynthesis.speak(speech);
    console.log("Speech synthesis started...");
}

window.speechSynthesis.onvoiceschanged = () => {
    console.log("Voices loaded.");
};

async function sol() {
    let text = document.getElementById('input').value;
    if (text.length === 0) return;
    
    output = document.createElement('p');
    output.className = 'user';
    chatui.appendChild(output);
    output.textContent = text;

    videoPlay(text);
}

function stop() {
    if (recognition) {
        window.speechSynthesis.cancel();
        document.getElementById("videoPlayer").pause();
        document.getElementById("videoPlayer").setAttribute("src", "static/videos/std2.mp4");
        document.getElementById("videoPlayer").play();
        if(output.innerHTML === 'Listening...')
        output.remove()
        isStopped = true; // Set flag to prevent restart
        recognition.stop(); // Stop recognition
        console.log("Speech recognition manually stopped.");
    }
}
