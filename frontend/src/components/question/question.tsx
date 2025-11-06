import type { QuestionType } from "../../views/DailyQuestions";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group"
import { Slider } from "../ui/slider";

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
        <h1>Frage {index+1} von {total}</h1>
        <p>{data.question}</p>
        {body(data)}
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

const body = (data: QuestionType) => {
  switch (data.type) {
    case 'text':
      return <Input />
    case 'enum':
      return (
         <RadioGroup>
          {data.options.map((option) => (
            <div className="flex items-center gap-3">
              <RadioGroupItem value={option.value.toString()} id={option.value.toString()} />
              <Label htmlFor="r1">{option.label}</Label>
            </div>
          ))}
         </RadioGroup>
      )
    case 'scale':
      return <Slider min={data.from} max={data.to} />
  } 
}

export default Question
