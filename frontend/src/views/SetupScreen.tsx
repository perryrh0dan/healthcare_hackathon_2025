import { Input } from '@/components/ui/input';
import { Button } from '../components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import useAuthedQuery from '@/hooks/useAuthedQuery';
import useAuthedMutation from '@/hooks/useAuthedMutation';
import { useAuth } from '@/contexts';

interface Question {
  question: string;
  type: string;
  options?: { label: string; value: string }[];
  field: string
  value?: string | number
}

const SetupScreen = () => {
  const navigate = useNavigate()

  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [file, setFile] = useState<File | null>(null);

  const { refresh } = useAuth()

  const {
    data: questions = [],
    isLoading,
    error,
  } = useAuthedQuery({
    queryKey: ['registration'],
    queryFn: async () => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/setup`);
      if (!response.ok) {
        throw new Error('Failed to fetch registration questions');
      }
      return response.json() as Promise<Question[]>;
    },
  });

  const { mutate: submitProfile } = useAuthedMutation({
    mutationKey: ['setup'],
    mutationFn: async (formData: FormData) => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/users/setup`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      if (!response.ok) {
        const error: any = new Error('Failed to update profile');
        error.response = response;
        throw error;
      }
    },
    onSuccess: async () => {
      await refresh()
      navigate({ to: '/home'})
    },
    onError: () => {
    },
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData();
    questions.forEach(question => {
      const value = answers[question.field]

      formData.append(question.field, value || question.value?.toString() || '' );
    })

    if (file) {
      formData.append('electronic_patient_record', file);
    }
    submitProfile(formData);
  };

  if (isLoading) return <div>Loading...</div>;

  if (error) return <div>Error loading questions</div>;

  return (
    <div className="w-full max-w-md">
      <div className="bg-card border-border flex flex-col items-center rounded-lg border p-6 shadow-lg">
        <h1 className="mb-8 text-center text-2xl font-bold">
          Setup Your Profile
        </h1>
        <form className="w-full max-w-sm space-y-4" onSubmit={handleSubmit}>
          {questions.map((question) => (
            <div key={question.field}>
              <Label htmlFor={`question-${question.field}`}>{question.question} *</Label>
              {question.type === 'text' ? (
                <Input
                  id={`question-${question.field}`}
                  type="text"
                  value={answers[question.field] || question.value}
                  onChange={(e) =>
                    setAnswers((prev) => ({ ...prev, [question.field]: e.target.value }))
                  }
                  onBlur={() =>
                    setTouched((prev) => ({ ...prev, [question.field]: true }))
                  }
                  required
                  className={
                    touched[question.field] && !answers[question.field] ? 'border-red-500' : ''
                  }
                />
              ) : question.type === 'number' ? (
                <Input
                  id={`question-${question.field}`}
                  type="number"
                  value={answers[question.field] || question.value}
                  onChange={(e) =>
                    setAnswers((prev) => ({ ...prev, [question.field]: e.target.value }))
                  }
                  onBlur={() =>
                    setTouched((prev) => ({ ...prev, [question.field]: true }))
                  }
                  required
                  className={
                    touched[question.field] && !answers[question.field] ? 'border-red-500' : ''
                  }
                />
              ) : question.type === 'enum' ? (
                <Select
                  value={answers[question.field] || question.value?.toString()}
                  onValueChange={(value) =>
                    setAnswers((prev) => ({ ...prev, [question.field]: value }))
                  }
                  required
                >
                  <SelectTrigger
                    id={`question-${question.field}`}
                    className={`h-12 w-full ${touched[question.field] && !answers[question.field] ? 'border-red-500' : ''}`}
                    onBlur={() =>
                      setTouched((prev) => ({ ...prev, [question.field]: true }))
                    }
                  >
                    <SelectValue placeholder="Select an option" />
                  </SelectTrigger>
                  <SelectContent>
                    {question.options?.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : null}
            </div>
          ))}
          <Label htmlFor="epr">Electronic Patient Record</Label>
          <Input
            type="file"
            id="epr"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <p className="text-muted-foreground text-sm">
            All fields marked with * are required.
          </p>
          <Button type="submit" className="w-full">
            Save Profile
          </Button>
        </form>
      </div>
    </div>
  );
};

export default SetupScreen;
