import type { QuestionType } from "../../views/DailyQuestions";
import { Button } from "../ui/button";
import { Input } from "../ui/input";

type QuestionProps = {
  data: QuestionType, 
  index: number, 
  total: number,
  onNext: () => void,
  onPrev: () => void,
}

const Question = ({ data, index, total, onNext, onPrev }: QuestionProps) => {
  return (
    <div>
      <div className="rounded-l p-4 flex flex-col gap-2">
        <h1>Frage {index} von {total}</h1>
        <p>{data.question}</p>
        { data.type === 'text' && (
          <Input />
        )}
        <div className="flex flex-row gap-2 w-full">
          <Button className="w-full" variant="outline" onClick={onPrev}>
            Prev
          </Button>
          <Button className="w-full" onClick={onNext}>
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}

export default Question
