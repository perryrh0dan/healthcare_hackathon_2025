import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Message from '@/components/ui/message';
import useAuthedMutation from '@/hooks/useAuthedMutation';

type ChatProps = {
  open: boolean
  onSend: () => void
}

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
}

const Chat = ({ open, onSend }: ChatProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');

  const sendMessageMutation = useAuthedMutation({
    mutationFn: async (message: string) => {
      const response = await fetch('/api/ws/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      return response.json();
    },
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { text: data.response, sender: 'bot' }]);
    },
  });

  const handleSend = () => {
    if (input.trim() && !sendMessageMutation.isPending) {
      onSend()
      setMessages((prev) => [...prev, { text: input, sender: 'user' }]);
      sendMessageMutation.mutate(input);
      setInput('');
    }
  };

  return (
    <div className="flex h-full flex-col">
      {open && (  <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, idx) => (
          <Message key={idx} text={msg.text} sender={msg.sender} />
        ))}
      </div>  )}
      <div className="fixed right-0 bottom-0 left-0 flex gap-2 border-t border-gray-300 bg-white p-4">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={sendMessageMutation.isPending}
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleSend();
          }}
        />
        <Button onClick={handleSend} disabled={sendMessageMutation.isPending}>
          Send
        </Button>
      </div>
    </div>
  );
};

export default Chat;
