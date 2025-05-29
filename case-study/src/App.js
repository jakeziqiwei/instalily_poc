import React, { useState } from "react";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import ChatArea from "./components/ChatArea";
import { theme } from "./styles/theme";
import { ThemeProvider } from "@mui/material/styles";

function App() {
  const [currentChat, setCurrentChat] = useState(null);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          height: "100vh",
          background: "337778",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 2,
        }}
      >
        <ChatArea chatId={currentChat} />
      </Box>
    </ThemeProvider>
  );
}

export default App;
