import { useState } from "react";
import { useQuery } from '@tanstack/react-query';
import IQuestion from "../components/question/question";
import Question from "../components/question/question";
import useAuthedMutation from "@/hooks/useAuthedMutation";
import { useNavigate } from "@tanstack/react-router";

interface IQuestion {
  question: string
}

export interface INumberQuestion extends IQuestion {
  type: 'number'
}

export interface ITextQuestion extends IQuestion {
  type: 'text'
}

export interface INumberQuestion extends IQuestion {
  type: 'number'
}

export interface IEnumQuestion extends IQuestion {
  type: 'enum'
  options: [{ label: string, value: string | number }]
}

export interface IScaleQuestion extends IQuestion {
  type: 'scale',
  from: number,
  to: number,
}

export type QuestionType = ITextQuestion | INumberQuestion | IEnumQuestion | IScaleQuestion | INumberQuestion


const DailyQuestions = () => {
  const navigate = useNavigate()
  const [index, setIndex] = useState<number>(0)

  const { data: questions = [], isLoading: isLoadingQuestions, error: errorQuestions } = useQuery({
    queryKey: ['daily-questions'],
    queryFn: async () => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/daily`, { credentials: 'include' });
      if (!response.ok) {
        throw new Error('Failed to fetch daily questions');
      }
      return response.json() as Promise<QuestionType[]>;
    },
  });
  
  const { mutate: submit } = useAuthedMutation({
    mutationKey: ['submit-daily-answers'],
    mutationFn: async (data: any) => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/daily`, { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data), 
        credentials: 'include' 
      });
      if (!response.ok) {
        throw new Error('Failed to fetch daily questions');
      }
      return response.json() as Promise<QuestionType[]>;
    },
    onSuccess: () => {
      navigate({ to: '/home' })
    }
  });

  if (isLoadingQuestions) return <div>Loading...</div>;
  if (errorQuestions) return <div>Error loading questions</div>;

  const question = questions[index]

  if (!question) return <div>No questions available</div>;

  const handleSubmit = (data: any) => {
    submit(data)
  }

  return (
    <Question
      data={question}
      index={index}
      total={questions.length}
      onPrev={() => setIndex(i => Math.max(0, i - 1))}
      onNext={() => setIndex(i => Math.min(questions.length - 1, i + 1))}
      onSubmit={(data) => handleSubmit(data)}
    />
  );
};

export default DailyQuestions;
