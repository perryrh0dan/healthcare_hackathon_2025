import { useState } from "react";
import { useQuery } from '@tanstack/react-query';
import IQuestion from "../components/question/question";
import Question from "../components/question/question";

interface IQuestion {
  question: string
}

interface NumberQuestion extends IQuestion {
  type: 'number'
}

interface TextQuestion extends IQuestion {
  type: 'text'
}

interface EnumQuestion extends IQuestion {
  type: 'enum'
  options: [{ label: string, value: string | number }]
}

interface ScaleQuestion extends IQuestion {
  type: 'scale',
  from: number,
  to: number,
}

export type QuestionType = TextQuestion | NumberQuestion | EnumQuestion | ScaleQuestion


const DailyQuestions = () => {
  const [index, setIndex] = useState<number>(0)

  const { data: questions = [], isLoading, error } = useQuery({
    queryKey: ['daily-questions'],
    queryFn: async () => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/daily`, { credentials: 'include' });
      if (!response.ok) {
        throw new Error('Failed to fetch daily questions');
      }
      return response.json() as Promise<QuestionType[]>;
    },
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading questions</div>;

  const question = questions[index]

  if (!question) return <div>No questions available</div>;

  return (
    <div>
      <Question
        data={question}
        index={index}
        total={questions.length}
        onPrev={() => setIndex(i => Math.max(0, i - 1))}
        onNext={() => setIndex(i => Math.min(questions.length - 1, i + 1))}/>
    </div>
  );
};

export default DailyQuestions;
