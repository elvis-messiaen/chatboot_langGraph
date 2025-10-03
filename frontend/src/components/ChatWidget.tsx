import { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendMessage } from '../services/api';
import Message from './Message';
import InputBox from './InputBox';

/**
 * Représente un message dans la conversation.
 */
interface MessageType {
  /** Contenu du message */
  content: string;
  /** Rôle : 'user' pour utilisateur, 'assistant' pour bot */
  role: 'user' | 'assistant';
  /** Timestamp de création (optionnel) */
  timestamp?: Date;
}

/**
 * Composant principal du chatbot.
 * Gère la conversation, l'état, et la communication avec le backend.
 */
const ChatWidget = () => {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    const generateSessionId = (): string => {
      const storageKey = 'chatbot_session_id';
      const storedId = localStorage.getItem(storageKey);

      if (storedId) {
        return storedId;
      }

      const newId = uuidv4();
      localStorage.setItem(storageKey, newId);
      return newId;
    };

    const initSession = async () => {
      const newSessionId = generateSessionId();
      setSessionId(newSessionId);

      // Appel initial au backend pour récupérer le message d'accueil de LangGraph
      try {
        const response = await sendMessage(newSessionId, "Bonjour", null);
        const backendWelcome: MessageType = {
          content: response.reponse,
          role: 'assistant',
          timestamp: new Date()
        };
        setMessages([backendWelcome]);
      } catch (error) {
        console.error('Erreur lors de l\'initialisation:', error);
        setMessages([{
          content: "Bonjour ! Je suis votre assistant virtuel. Comment puis-je vous aider aujourd'hui ?",
          role: 'assistant',
          timestamp: new Date()
        }]);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, []);

  const handleSendMessage = async (messageContent: string) => {
    const userMessage: MessageType = {
      content: messageContent,
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(sessionId, messageContent, null);

      const botMessage: MessageType = {
        content: response.reponse,
        role: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);

      const errorMessage: MessageType = {
        content: 'Désolé, une erreur est survenue. Peux-tu réessayer ?',
        role: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);

    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="w-full max-w-4xl h-[85vh] flex flex-col bg-white rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-violet-600 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">Chatbot LangGraph</h1>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                <p className="text-xs text-white/80">En ligne</p>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 bg-slate-50">
          {messages.map((msg, index) => (
            <Message
              key={index}
              message={msg.content}
              isUser={msg.role === 'user'}
            />
          ))}

          {isLoading && (
            <div className="flex justify-start mb-6">
              <div className="bg-white border border-slate-200 shadow-sm px-5 py-3 rounded-2xl">
                <p className="text-sm text-slate-600">Rédaction en cours...</p>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-slate-200 bg-white">
          <InputBox onSend={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default ChatWidget;