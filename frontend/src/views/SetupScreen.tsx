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
import { useQuery, useMutation } from '@tanstack/react-query';

interface Question {
  question: string;
  type: string;
  options?: { label: string; value: string }[];
}

const SetupScreen = () => {
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [touched, setTouched] = useState<Record<number, boolean>>({});
  const [fileTouched, setFileTouched] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const {
    data: questions = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['registration'],
    queryFn: async () => {
      const response = await fetch(`http://localhost:8008/registration`);
      if (!response.ok) {
        throw new Error('Failed to fetch registration questions');
      }
      return response.json() as Promise<Question[]>;
    },
  });

  const { mutate: submitProfile } = useMutation({
    mutationKey: ['submit-profile'],
    mutationFn: async (formData: FormData) => {
      const response = await fetch('http://localhost:8008/submit-profile', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error('Failed to submit profile');
      }
    },
    onSuccess: () => {
      alert('Profile submitted successfully!');
    },
    onError: () => {
      alert('Error submitting profile.');
    },
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData();
    questions.forEach((_, idx) => {
      formData.append(`answer_${idx}`, answers[idx] || '');
    });
    if (file) {
      formData.append('electronic_patient_record', file);
    }
    submitProfile(formData);
  };

  if (isLoading) return <div>Loading...</div>;

  if (error) return <div>Error loading questions</div>;

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center rounded-md bg-white p-4">
        <h1 className="mb-8 text-center text-2xl font-bold">
          Setup Your Profile
        </h1>
        <form className="w-full max-w-sm space-y-4" onSubmit={handleSubmit}>
          {questions.map((question, idx) => (
            <div key={idx}>
              <Label htmlFor={`question-${idx}`}>{question.question} *</Label>
              {question.type === 'text' ? (
                <Input
                  id={`question-${idx}`}
                  type="text"
                  value={answers[idx] || ''}
                  onChange={(e) =>
                    setAnswers((prev) => ({ ...prev, [idx]: e.target.value }))
                  }
                  onBlur={() =>
                    setTouched((prev) => ({ ...prev, [idx]: true }))
                  }
                  required
                  className={
                    touched[idx] && !answers[idx] ? 'border-red-500' : ''
                  }
                />
              ) : question.type === 'number' ? (
                <Input
                  id={`question-${idx}`}
                  type="number"
                  value={answers[idx] || ''}
                  onChange={(e) =>
                    setAnswers((prev) => ({ ...prev, [idx]: e.target.value }))
                  }
                  onBlur={() =>
                    setTouched((prev) => ({ ...prev, [idx]: true }))
                  }
                  required
                  className={
                    touched[idx] && !answers[idx] ? 'border-red-500' : ''
                  }
                />
              ) : question.type === 'enum' ? (
                <Select
                  value={answers[idx] || ''}
                  onValueChange={(value) =>
                    setAnswers((prev) => ({ ...prev, [idx]: value }))
                  }
                  required
                >
                  <SelectTrigger
                    id={`question-${idx}`}
                    className={`h-12 w-full ${touched[idx] && !answers[idx] ? 'border-red-500' : ''}`}
                    onBlur={() =>
                      setTouched((prev) => ({ ...prev, [idx]: true }))
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
          <Label htmlFor="epr">Electronic Patient Record *</Label>
          <Input
            type="file"
            id="epr"
            required
            className={fileTouched && !file ? 'border-red-500' : ''}
            onBlur={() => setFileTouched(true)}
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <p className="text-sm text-gray-600">
            All fields marked with * are required.
          </p>
          <Button type="submit" className="h-12 w-full">
            Save Profile
          </Button>
        </form>
      </div>
    </div>
  );
};

export default SetupScreen;
