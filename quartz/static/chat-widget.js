/**
 * Wiki Chat Widget — floating chat button + slide-out panel
 * Connects to local wiki API server (wiki serve)
 */
(function () {
  const API_URL = "http://localhost:8000";

  // Get current page slug from URL path
  function getCurrentPage() {
    const path = window.location.pathname
      .replace(/^\/knowledge-base\//, "")
      .replace(/\/$/, "")
      .replace(/\.html$/, "");
    return path || null;
  }

  // Inject styles
  const style = document.createElement("style");
  style.textContent = `
    #wiki-chat-btn {
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: var(--secondary, #284b63);
      color: white;
      border: none;
      cursor: pointer;
      font-size: 24px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.2s;
    }
    #wiki-chat-btn:hover { transform: scale(1.1); }

    #wiki-chat-panel {
      position: fixed;
      bottom: 90px;
      right: 24px;
      width: 400px;
      max-height: 520px;
      background: var(--light, #faf8f8);
      border: 1px solid var(--lightgray, #e5e5e5);
      border-radius: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.18);
      z-index: 9998;
      display: none;
      flex-direction: column;
      font-family: var(--bodyFont, 'Source Sans Pro', sans-serif);
      overflow: hidden;
    }
    #wiki-chat-panel.open { display: flex; }

    #wiki-chat-header {
      padding: 14px 16px;
      background: var(--secondary, #284b63);
      color: white;
      font-weight: 600;
      font-size: 15px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    #wiki-chat-status { opacity: 0.7; font-size: 12px; font-weight: 400; }

    #wiki-chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 12px 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      min-height: 200px;
      max-height: 340px;
    }

    .chat-msg {
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 14px;
      line-height: 1.5;
      max-width: 90%;
      word-wrap: break-word;
    }
    .chat-msg.user {
      background: var(--secondary, #284b63);
      color: white;
      align-self: flex-end;
      border-bottom-right-radius: 4px;
    }
    .chat-msg.bot {
      background: var(--lightgray, #e5e5e5);
      color: var(--darkgray, #4e4e4e);
      align-self: flex-start;
      border-bottom-left-radius: 4px;
    }
    .chat-msg.error {
      background: #fee;
      color: #c33;
      align-self: center;
      font-size: 13px;
    }

    .chat-save-btn {
      background: none;
      border: 1px solid var(--gray, #b8b8b8);
      border-radius: 6px;
      padding: 3px 10px;
      font-size: 12px;
      cursor: pointer;
      margin-top: 6px;
      color: var(--darkgray, #4e4e4e);
      display: block;
    }
    .chat-save-btn:hover { background: var(--lightgray, #e5e5e5); }
    .chat-save-btn.saved {
      border-color: var(--secondary, #284b63);
      color: var(--secondary, #284b63);
      cursor: default;
    }

    #wiki-chat-input-area {
      display: flex;
      padding: 10px 12px;
      border-top: 1px solid var(--lightgray, #e5e5e5);
      gap: 8px;
    }
    #wiki-chat-input {
      flex: 1;
      border: 1px solid var(--lightgray, #e5e5e5);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 14px;
      outline: none;
      background: var(--light, #faf8f8);
      color: var(--darkgray, #4e4e4e);
    }
    #wiki-chat-input:focus { border-color: var(--secondary, #284b63); }
    #wiki-chat-send {
      background: var(--secondary, #284b63);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 8px 16px;
      cursor: pointer;
      font-size: 14px;
    }
    #wiki-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }

    .chat-typing {
      font-size: 13px;
      color: var(--gray, #b8b8b8);
      font-style: italic;
      padding: 4px 14px;
    }

    @media (max-width: 500px) {
      #wiki-chat-panel {
        width: calc(100vw - 32px);
        right: 16px;
        bottom: 80px;
      }
    }
  `;
  document.head.appendChild(style);

  // Create button
  const btn = document.createElement("button");
  btn.id = "wiki-chat-btn";
  btn.textContent = "\uD83D\uDCAC"; // speech bubble emoji
  btn.title = "Ask your knowledge base";
  document.body.appendChild(btn);

  // Create panel using DOM methods (no innerHTML)
  const panel = document.createElement("div");
  panel.id = "wiki-chat-panel";

  const header = document.createElement("div");
  header.id = "wiki-chat-header";
  const headerTitle = document.createTextNode("Wiki Chat");
  const headerStatus = document.createElement("span");
  headerStatus.id = "wiki-chat-status";
  headerStatus.textContent = "powered by wiki serve";
  header.appendChild(headerTitle);
  header.appendChild(headerStatus);

  const messagesDiv = document.createElement("div");
  messagesDiv.id = "wiki-chat-messages";

  const inputArea = document.createElement("div");
  inputArea.id = "wiki-chat-input-area";
  const input = document.createElement("input");
  input.id = "wiki-chat-input";
  input.type = "text";
  input.placeholder = "Ask your knowledge base...";
  const sendBtn = document.createElement("button");
  sendBtn.id = "wiki-chat-send";
  sendBtn.textContent = "Send";
  inputArea.appendChild(input);
  inputArea.appendChild(sendBtn);

  panel.appendChild(header);
  panel.appendChild(messagesDiv);
  panel.appendChild(inputArea);
  document.body.appendChild(panel);

  // Toggle panel
  btn.addEventListener("click", function () {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) {
      input.focus();
    }
  });

  function addMessage(text, type) {
    var msg = document.createElement("div");
    msg.className = "chat-msg " + type;
    msg.textContent = text;

    if (type === "bot") {
      var saveBtn = document.createElement("button");
      saveBtn.className = "chat-save-btn";
      saveBtn.textContent = "Save to wiki";
      saveBtn.addEventListener("click", function () {
        saveAnswer(saveBtn);
      });
      msg.appendChild(saveBtn);
    }

    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return msg;
  }

  function saveAnswer(saveBtnEl) {
    if (saveBtnEl.classList.contains("saved")) return;
    saveBtnEl.textContent = "Saving...";

    // Find the last user question
    var userMsgs = messagesDiv.querySelectorAll(".chat-msg.user");
    var lastQuestion = userMsgs.length > 0
      ? userMsgs[userMsgs.length - 1].textContent
      : "Saved query";

    fetch(API_URL + "/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: lastQuestion, save: true, current_page: getCurrentPage() }),
    })
      .then(function () {
        saveBtnEl.textContent = "Saved!";
        saveBtnEl.classList.add("saved");
      })
      .catch(function () {
        saveBtnEl.textContent = "Save failed";
      });
  }

  function sendQuery() {
    var question = input.value.trim();
    if (!question) return;

    input.value = "";
    sendBtn.disabled = true;
    addMessage(question, "user");

    // Typing indicator
    var typing = document.createElement("div");
    typing.className = "chat-typing";
    typing.textContent = "Thinking...";
    messagesDiv.appendChild(typing);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    fetch(API_URL + "/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, save: false, current_page: getCurrentPage() }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Server error: " + res.status);
        return res.json();
      })
      .then(function (data) {
        typing.remove();
        addMessage(data.answer, "bot");
      })
      .catch(function (err) {
        typing.remove();
        if (err.message.indexOf("Failed to fetch") !== -1 || err.message.indexOf("NetworkError") !== -1) {
          addMessage('Cannot reach wiki server. Run "wiki serve" to start it.', "error");
        } else {
          addMessage("Error: " + err.message, "error");
        }
      })
      .finally(function () {
        sendBtn.disabled = false;
        input.focus();
      });
  }

  sendBtn.addEventListener("click", sendQuery);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuery();
    }
  });
})();
