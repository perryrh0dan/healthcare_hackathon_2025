import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Message from '@/components/ui/message';
import useAuthedMutation from '@/hooks/useAuthedMutation';
import { ChevronDown, ChevronUp, Loader, Camera } from 'lucide-react';
import Cookies from 'js-cookie';

type ChatProps = {
  open: boolean;
  onSend: () => void;
  onClose: () => void;
  onOpen: () => void;
};

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
}

const Chat = ({ open, onSend, onClose, onOpen }: ChatProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessageMutation = useAuthedMutation({
    mutationFn: async (message: string) => {
      const conversationId = Cookies.get('conversation_id');

      const formData = new FormData();
      formData.append('message', message);

      if (conversationId) formData.append('conversation_id', conversationId);
      if (selectedFile) formData.append('file', selectedFile);

      const response = await fetch('/api/chat', {
        method: 'POST',
        body: formData,
      });
      return response.json();
    },
    onSuccess: (data: {
      conversation_id?: string;
      history: { role: string; content: string }[];
    }) => {
      if (data.conversation_id) {
        Cookies.set('conversation_id', data.conversation_id, { expires: 7 });
      }
      setMessages(
        data.history.map((item) => ({
          text: item.content,
          sender: item.role === 'assistant' ? 'bot' : 'user',
        }))
      );
    },
  });

  const handleSend = () => {
    if ((input.trim() || selectedFile) && !sendMessageMutation.isPending) {
      onSend();
      setMessages((prev) => [...prev, { text: input, sender: 'user' }]);
      sendMessageMutation.mutate(input);
      setInput('');
      setSelectedFile(null);
    }
  };

  const handleToggle = () => {
    if (open) {
      onClose();
    } else {
      onOpen();
    }
  };

  return (
    <div
      className={`absolute ${open ? 'top-0 right-0 bottom-0 left-0' : ''} bg-white`}
    >
      <div
        className={`fixed right-0 bottom-0 left-0 ${open ? 'top-0' : ''} flex gap-2 border-t border-gray-300 bg-white`}
      >
        <div className="relative flex h-full w-full flex-col p-4">
          {open ? (
            <div className="absolute top-5 left-1/2 flex h-10 -translate-x-1/2 items-center justify-center">
              <Button onClick={handleToggle} className="rounded-full">
                {<ChevronDown size={20} />}
              </Button>
            </div>
          ) : (
            <div className="absolute -top-5 left-1/2 flex h-10 -translate-x-1/2 items-center justify-center">
              <Button onClick={handleToggle} className="rounded-full">
                {<ChevronUp size={20} />}
              </Button>
            </div>
          )}
          {open && (
            <div className="flex-1 overflow-y-auto p-4">
              {messages.map((msg, idx) => (
                <Message key={idx} text={msg.text} sender={msg.sender} />
              ))}
              {sendMessageMutation.isPending && (
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader className="animate-spin" size={16} />
                  AI is thinking...
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
          {selectedFile && (
            <div className="flex items-center gap-2 border-t p-2">
              <img
                src={URL.createObjectURL(selectedFile)}
                alt="Selected"
                className="h-16 w-16 rounded object-cover"
              />
              <span className="text-sm text-gray-600">{selectedFile.name}</span>
              <Button
                onClick={() => setSelectedFile(null)}
                variant="ghost"
                size="sm"
                className="text-red-500"
              >
                ✕
              </Button>
            </div>
          )}
          <div className="flex w-full gap-2">
            <Button
              onClick={() => fileInputRef.current?.click()}
              variant="ghost"
              size="icon"
              className="shrink-0"
            >
              <Camera size={20} />
            </Button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              accept="image/*"
              style={{ display: 'none' }}
            />
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              disabled={sendMessageMutation.isPending}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSend();
              }}
            />
            <Button
              onClick={handleSend}
              disabled={sendMessageMutation.isPending}
            >
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
