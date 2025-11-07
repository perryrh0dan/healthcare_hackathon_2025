import type { IEnumQuestion } from "@/views/DailyQuestions"
import { Button } from "../ui/button"
import { useState } from "react"

type EnumQuestionProps = {
  options: IEnumQuestion['options']
  onChange: (value: any) => void
}

const EnumQuestion = ({ options, onChange }: EnumQuestionProps) => {
  const [active, setActive] = useState<string | number>()

  const handleClick = (value: string | number) => {
    setActive(value)
    onChange(value)
  }

  return (
    <div className="flex flex-col h-full gap-2">
      {options.map((option) => (
        <Button onClick={() => handleClick(option.value)} className="w-full" variant={active === option.value ? 'default' : 'outline'}>
          {option.label}
        </Button>
      ))}
    </div>
  )

}

export default EnumQuestion
