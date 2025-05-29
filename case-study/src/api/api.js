const API_URL = "http://localhost:8000/api/v1/chat";

export const getAIMessage = async (userQuery, conversationHistory = []) => {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: userQuery,
        conversation_history: conversationHistory,
      }),
    });
    console.log("Response:", response);
    const data = await response.json();
    return {
      role: "assistant",
      content: data.response,
    };
  } catch (error) {
    console.error("Error fetching AI message:", error);
    return {
      role: "assistant",
      content: "Sorry, I'm having connection issues. Please try again.",
    };
  }
};
