import React from 'react';

interface MessageProps {
  text: string;
  sender: 'user' | 'bot';
  image?: string;
}

const Message: React.FC<MessageProps> = ({ image, text, sender }) => {
  return (
    <div
      className={`mb-2 flex ${sender === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-xs rounded-lg px-4 py-2 ${
          sender === 'user'
            ? 'bg-blue-500 text-white'
            : 'bg-gray-200 text-gray-800'
        }`}
      >
        <span>{text}</span>
        { image !== undefined && image !== null && ( <img src={`/api/${image}`} /> ) }
      </div>
    </div>
  );
};

export default Message;
