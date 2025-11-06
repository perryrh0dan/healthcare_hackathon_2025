import type { QuestionType } from "../../views/DailyQuestions";

type QuestionProps = {
  data: QuestionType, 
  index: number, 
  total: number,
  onNext: () => void,
  onPrev: () => void,
}

const Question = ({ data, index, total}: QuestionProps) => {
  return (
    <div>
      <div className="rounded-l p-4 flex flex-col gap-2">
        <h1>Frage {index} von {total}</h1>
        <p>{data.question}</p>
        { data.type === 'text' && (
          <input />
        )}
        <div className="flex flex-row gap-2 w-full">
          <button className="w-full">Prev</button>
          <button className="w-full">Next</button>
        </div>
      </div>
    </div>
  );
}

export default Question
