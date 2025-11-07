import { useState } from "react";
import type { QuestionType } from "../../views/DailyQuestions";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Slider } from "../ui/slider";
import EnumQuestion from "./enum-question";

type QuestionAnswer = {
  question: string,
  answer: string | number
}

type QuestionProps = {
  data: QuestionType, 
  index: number, 
  total: number,
  onNext: () => void,
  onPrev: () => void,
  onSubmit: (data: Array<QuestionAnswer>) => void,
}

const Question = ({ data, index, total, onNext, onPrev, onSubmit }: QuestionProps) => {
  const [answers, setAnswers] = useState<Array<QuestionAnswer>>([])

  const percentage = (index + 1) / total

  const handleSubmit = () => {
    onSubmit(answers)
  }

  const handleChange = (answer: string | number) => {
    const newAnswers = [...answers]

    newAnswers[index] = { question: data.question, answer: answer }

    setAnswers(newAnswers)
  }

  const answer: QuestionAnswer | undefined = answers[index]

  const body = (data: QuestionType) => {
    switch (data.type) {
      case 'text':
        return <Input value={answer?.answer} autoFocus={true} key={data.question} onChange={(e) => handleChange(e.target.value)} />
      case 'enum':
        return (
          <EnumQuestion value={answer?.answer} key={data.question} options={ data.options } onChange={handleChange} />
        )
      case 'scale':
        return <Slider value={[ answer === undefined ? data.from : typeof answer?.answer === 'string' ? parseInt(answer.answer) : answer.answer ]} key={data.question} min={data.from} max={data.to} onChange={(e) => handleChange((e.target as any).value)} />
      case 'number':
        return <Input value={answer?.answer} autoFocus={true} key={data.question} type="number" onChange={(e) => handleChange(e.target.value)} />
    } 
  }

  const handleNext = () => {
    if (answers[index]) {
      onNext()
    }
  }

  return (
    <div className="p-4 flex flex-col gap-6 h-full w-full grow">
      <h1>Frage {index+1} von {total}</h1>
      <div className="h-2 w-full bg-gray-200 rounded-md overflow-hidden">
        <div className="h-full bg-red-300" style={{ width: `${percentage * 100}%`}}></div>
      </div>
      <div className="flex justify-center my-8">
        <h1 className="text-xl font-bold">{data.question}</h1>
      </div>
      <div className="flex-1 h-full">
        {body(data)}
      </div>
      <div className="flex flex-row gap-2 w-full">
        <Button className="w-full" variant="outline" onClick={onPrev}>
          Prev
        </Button>
        { index === total - 1 ? (
          <Button className="w-full" onClick={handleSubmit}>
            Submit
          </Button>
        ) : (
          <Button className="w-full" onClick={handleNext}>
            Next
          </Button>
        )}
      </div>
    </div>
  );
}


export default Question
