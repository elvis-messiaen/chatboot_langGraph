import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface ChatResponse {
  reponse: string;
  lead_sauvegarde: boolean;
  score: number | null;
  informations_manquantes: string[];
  intention_detectee: string | null;
}

export const sendMessage = async (
  sessionId: string,
  message: string,
  nom: string | null = null
): Promise<ChatResponse> => {
  try {
    const response = await axios.post<ChatResponse>(`${API_BASE_URL}/api/chat`, {
      session_id: sessionId,
      message: message,
      nom: nom
    });
    return response.data;
  } catch (error) {
    console.error('Erreur lors de l\'envoi du message:', error);
    throw error;
  }
};

export const checkHealth = async (): Promise<{ status: string } | null> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    console.error('API non accessible:', error);
    return null;
  }
};