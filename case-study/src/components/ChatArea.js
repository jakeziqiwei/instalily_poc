import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Grid,
  CircularProgress,
  Fade,
  Container,
} from "@mui/material";
import logo from "../assets/logo.svg";
import { Send as SendIcon } from "@mui/icons-material";

const ChatArea = ({ chatId }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = { role: "user", content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/v1/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: inputValue,
          user_id: "user123",
          conversation_history: [],
        }),
      });

      const data = await response.json();
      const assistantMessage = { role: "assistant", content: data.response };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const examples = `
- Find dishwasher rack parts
- PS12586284 water filter
- How can I fix my dishwasher
  `;

  const capabilities = `
- Search for specific parts by ID or description
- Find repair guides and troubleshooting tips
- Check part compatibility with your model
  `;

  const limitations = `
- Only covers refrigerator and dishwasher parts
- May not have all part numbers in database
- Cannot process orders directly
  `;

  if (messages.length === 0) {
    return (
      <Paper
        elevation={24}
        sx={{
          width: "100%",
          maxWidth: 1200,
          height: "90vh",
          borderRadius: 4,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          background: "linear-gradient(to bottom, #ffffff, #f8f9fa)",
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 4,
            textAlign: "center",
            borderBottom: "1px solid #e0e0e0",
            background: "white",
          }}
        >
          <img
            src={logo}
            alt="PartSelect Assistant"
            style={{ width: 250, paddingLeft: 42, paddingBottom: 10 }}
          />
          <Typography variant="h1" gutterBottom color="text.primary">
            PartSelect Assistant
          </Typography>
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ maxWidth: 600, mx: "auto" }}
          >
            Get instant answers, repair guides and part recommendations for your
            refrigerator and dishwasher needs.
          </Typography>
        </Box>

        <Box
          sx={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            paddingLeft: 12,
          }}
        >
          <Container>
            <Grid container spacing={10}>
              <Grid item xs={10} md={3}>
                <Box sx={{ mb: 3 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    color="text.primary"
                    sx={{ mb: 3, fontWeight: 600 }}
                  >
                    Examples
                  </Typography>
                  <Box sx={{ textAlign: "center", maxWidth: 280, mx: "auto" }}>
                    <ReactMarkdown>{examples}</ReactMarkdown>
                  </Box>
                </Box>
              </Grid>

              {/* Capabilities */}
              <Grid item xs={12} md={3}>
                <Box sx={{ mb: 4 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    color="text.primary"
                    sx={{ mb: 3, fontWeight: 600 }}
                  >
                    Capabilities
                  </Typography>
                  <Box sx={{ textAlign: "center", maxWidth: 280, mx: "auto" }}>
                    <ReactMarkdown>{capabilities}</ReactMarkdown>
                  </Box>
                </Box>
              </Grid>

              {/* Limitations */}
              <Grid item xs={12} md={3}>
                <Box sx={{ mb: 4 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    color="text.primary"
                    sx={{ mb: 3, fontWeight: 600 }}
                  >
                    Limitations
                  </Typography>
                  <Box sx={{ textAlign: "left", maxWidth: 280, mx: "auto" }}>
                    <ReactMarkdown>{limitations}</ReactMarkdown>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Container>
        </Box>

        {/* Input Area */}
        <Box
          sx={{
            p: 3,
            borderTop: "1px solid #e0e0e0",
            background: "white",
          }}
        >
          <Container maxWidth="md">
            <Box sx={{ position: "relative" }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Enter a prompt here..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                disabled={isLoading}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    paddingRight: "60px",
                    backgroundColor: "#f8f9fa",
                    "&:hover": {
                      backgroundColor: "white",
                    },
                    "&.Mui-focused": {
                      backgroundColor: "white",
                    },
                  },
                }}
              />
              <IconButton
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                sx={{
                  position: "absolute",
                  right: 8,
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "#FFA500",
                  color: "white",
                  width: 40,
                  height: 40,
                  "&:hover": {
                    background: "#FF8C00",
                    transform: "translateY(-50%) scale(1.05)",
                  },
                  "&:disabled": {
                    background: "#e0e0e0",
                    color: "#9e9e9e",
                  },
                }}
              >
                {isLoading ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  <SendIcon />
                )}
              </IconButton>
            </Box>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{
                display: "block",
                textAlign: "center",
                mt: 2,
                maxWidth: 600,
                mx: "auto",
              }}
            >
              PartSelect Assistant can make mistakes. Please verify part
              compatibility before ordering.
            </Typography>
          </Container>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper
      elevation={24}
      sx={{
        width: "100%",
        maxWidth: 1200,
        height: "90vh",
        borderRadius: 4,
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      {/* Messages */}
      <Box sx={{ flex: 1, overflow: "auto", p: 3 }}>
        {messages.map((message, index) => (
          <Fade in={true} key={index} timeout={500}>
            <Box
              sx={{
                display: "flex",
                justifyContent:
                  message.role === "user" ? "flex-end" : "flex-start",
                mb: 2,
              }}
            >
              <Paper
                elevation={1}
                sx={{
                  maxWidth: "70%",
                  p: 2,
                  borderRadius: 3,
                  background: message.role === "user" ? "#FFA500" : "#f8f9fa",
                  color: message.role === "user" ? "white" : "text.primary",
                }}
              >
                {message.role === "assistant" ? (
                  <Box
                    sx={{
                      "& p": { margin: "8px 0" },
                      "& ul": {
                        paddingLeft: "0px",
                        margin: "8px 0",
                        listStyle: "none",
                        listStyleType: "none",
                      },
                      "& ol": {
                        paddingLeft: "0px",
                        margin: "8px 0",
                        listStyle: "none",
                        listStyleType: "none",
                      },
                      "& li": {
                        marginBottom: "4px",
                        listStyle: "none",
                        listStyleType: "none",
                        "&::before": {
                          display: "none",
                        },
                        "&::marker": {
                          display: "none",
                        },
                      },
                      "& strong": { fontWeight: 600 },
                      "& a": { color: "#667eea", textDecoration: "none" },
                      "& a:hover": { textDecoration: "underline" },
                    }}
                  >
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </Box>
                ) : (
                  <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                    {message.content}
                  </Typography>
                )}
              </Paper>
            </Box>
          </Fade>
        ))}
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 2 }}>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                borderRadius: 3,
                background: "#f8f9fa",
                display: "flex",
                alignItems: "center",
                gap: 1,
              }}
            >
              <CircularProgress size={16} />
              <Typography variant="body2" color="text.secondary">
                Thinking...
              </Typography>
            </Paper>
          </Box>
        )}
      </Box>

      {/* Input Area */}
      <Box
        sx={{
          p: 3,
          borderTop: "1px solid #e0e0e0",
          background: "white",
        }}
      >
        <Box sx={{ position: "relative" }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Enter a prompt here..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            sx={{
              "& .MuiOutlinedInput-root": {
                paddingRight: "60px",
                backgroundColor: "#f8f9fa",
                "&:hover": {
                  backgroundColor: "white",
                },
                "&.Mui-focused": {
                  backgroundColor: "white",
                },
              },
            }}
          />
          <IconButton
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            sx={{
              position: "absolute",
              right: 8,
              top: "50%",
              transform: "translateY(-50%)",
              background: "#FFA500",
              color: "white",
              width: 40,
              height: 40,
              "&:hover": {
                background: "#FF8C00",
                transform: "translateY(-50%) scale(1.05)",
              },
              "&:disabled": {
                background: "#e0e0e0",
                color: "#9e9e9e",
              },
            }}
          >
            {isLoading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              <SendIcon />
            )}
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};

export default ChatArea;
