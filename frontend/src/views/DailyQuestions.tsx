import { useState } from "react";
import IQuestion from "../components/question/question";
import Question from "../components/question/question";

interface IQuestion {
  question: string
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

export type QuestionType = TextQuestion | EnumQuestion | ScaleQuestion


const DailyQuestions = () => {
  const [index, setIndex] = useState<number>(0)

  const questions: Array<QuestionType> = [{
    question: "Wie geht es dir heute",
    type: 'text',
  } as const]

  const question = questions[index]

  return (
    <div>
      <Question 
        data={question} 
        index={0} 
        total={questions.length}
        onPrev={() => setIndex(i => i - 1)} 
        onNext={() => setIndex(i => i + 1)}/>
    </div>
  );
};

export default DailyQuestions;
