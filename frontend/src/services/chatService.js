import api from "./api";

export async function sendMessage(message, lang = "fr") {
  const response = await api.post("/chat", {
    message,
    lang,
  });

  return response.data;
}
