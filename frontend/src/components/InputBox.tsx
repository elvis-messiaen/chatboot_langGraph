import { useState, type FormEvent } from 'react';

/**
 * Props du composant InputBox
 */
interface InputBoxProps {
  /** Fonction appelée lors de l'envoi d'un message */
  onSend: (message: string) => void;
  /** Indique si la saisie est désactivée */
  disabled: boolean;
}

/**
 * Composant de saisie de message pour le chatbot.
 * Gère l'input utilisateur et l'envoi de messages.
 */
const InputBox = ({ onSend, disabled }: InputBoxProps) => {
  const [input, setInput] = useState<string>('');

  /**
   * Gère la soumission du formulaire.
   * Envoie le message si le champ n'est pas vide et non désactivé.
   */
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex gap-3 p-6"
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Écrivez votre message..."
        disabled={disabled}
        className="flex-1 px-5 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-50 disabled:cursor-not-allowed text-slate-900 placeholder-slate-400"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="px-8 py-3 bg-gradient-to-r from-blue-600 to-violet-600 text-white font-medium rounded-xl hover:from-blue-700 hover:to-violet-700 disabled:from-slate-300 disabled:to-slate-300 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40"
      >
        Envoyer
      </button>
    </form>
  );
};

export default InputBox;