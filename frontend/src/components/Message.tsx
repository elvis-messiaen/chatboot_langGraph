import { type ReactNode } from 'react';

/**
 * Props du composant Message
 */
interface MessageProps {
  /** Contenu du message à afficher */
  message: string;
  /** True si c'est un message utilisateur, false si c'est le bot */
  isUser: boolean;
}

/**
 * Composant pour afficher un message dans le chat.
 * Stylisé différemment selon qu'il provient de l'utilisateur ou du bot.
 */
const Message = ({ message, isUser }: MessageProps): ReactNode => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div
        className={`max-w-2xl px-5 py-3 rounded-2xl shadow-sm ${
          isUser
            ? 'bg-gradient-to-br from-blue-600 to-violet-600 text-white'
            : 'bg-white border border-slate-200 text-slate-900'
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message}</p>
      </div>
    </div>
  );
};

export default Message;