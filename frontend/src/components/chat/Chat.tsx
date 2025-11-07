import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Message from '@/components/ui/message';
import useAuthedMutation from '@/hooks/useAuthedMutation';
import { ChevronDown, ChevronUp } from 'lucide-react';

type ChatProps = {
  open: boolean
  onSend: () => void
  onClose: () => void
  onOpen: () => void
}

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
}

const Chat = ({ open, onSend, onClose, onOpen }: ChatProps) => {
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

  const handleToggle = () => {
    if (open) {
      onClose()
    } else {
      onOpen()
    }
  }

  return (
    <div className={ `absolute ${open ? 'top-0 left-0 right-0 bottom-0' : '' }  bg-white` }>
      <div className={ `fixed right-0 bottom-0 left-0 ${open ? 'top-0' : ''} border-t border-gray-300 bg-white flex gap-2` }>
        <div className='flex flex-col w-full relative h-full p-4'>
          { open ? (
            <div className='absolute top-5 h-10 flex items-center justify-center left-1/2 -translate-x-1/2'>
              <Button
                onClick={handleToggle}
                className="rounded-full"
              >
                {<ChevronDown size={20} />}
              </Button>
            </div>
          ) : (
            <div className='absolute -top-5 h-10 flex items-center justify-center left-1/2 -translate-x-1/2'>
              <Button
                onClick={handleToggle}
                className="rounded-full"
              >
                {<ChevronUp size={20} />}
              </Button>
            </div>
          )}
          {open && (  <div className="flex-1 overflow-y-auto p-4">
            {messages.map((msg, idx) => (
              <Message key={idx} text={msg.text} sender={msg.sender} />
            ))}
          </div>  )}
          <div className='flex gap-2 w-full'>
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
      </div>
    </div>
  );
};

export default Chat;
