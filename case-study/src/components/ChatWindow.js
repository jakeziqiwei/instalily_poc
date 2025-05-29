import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";

function ChatWindow() {
  const defaultMessage = [
    {
      role: "assistant",
      content:
        "Hi, I'm the PartSelect Agent Helper. How can I help you today? Currently, I can help you find parts for your refrigerator or dishwasher as well as help you with your transactions.",
    },
  ];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (input) => {
    if (input.trim() !== "") {
      const newUserMessage = { role: "user", content: input };
      setMessages((prevMessages) => [...prevMessages, newUserMessage]);
      setInput("");

      const conversationHistory = [...messages.slice(1), newUserMessage];
      const newMessage = await getAIMessage(input, conversationHistory);
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    }
  };

  return (
    <div className="messages-container">
      {messages.map((message, index) => (
        <div key={index} className={`${message.role}-message-container`}>
          {message.content && (
            <div className={`message ${message.role}-message`}>
              <Markdown>{message.content}</Markdown>
            </div>
          )}
        </div>
      ))}
      <div ref={messagesEndRef} />
      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend(input);
              e.preventDefault();
            }
          }}
          rows="3"
        />
        <button className="send-button" onClick={() => handleSend(input)}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
