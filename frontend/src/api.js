import axios from "axios" 

const API_BASE_URL = import.meta.env.VITE_API_URL;
const API_KEY = "sk_track2_987654321";

export const analyzeDocument = async (payload) => {
  const response = await axios.post(
    `${API_BASE_URL}/document-analyze`,
    payload,
  
  );

  return response.data;
};