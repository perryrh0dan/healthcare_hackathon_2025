import { useState } from 'react';
import { Calendar } from '../components/ui/calendar';
import { format } from 'date-fns';

const FoodPlanner = () => {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>();

  // Sample meal data - in a real app, this would come from an API or context
  const meals = {
    [format(new Date(), 'yyyy-MM-dd')]: {
      breakfast: 'Oatmeal with fruits',
      lunch: 'Grilled chicken salad',
      dinner: 'Salmon with vegetables',
    },
    [format(new Date(Date.now() + 86400000), 'yyyy-MM-dd')]: {
      breakfast: 'Greek yogurt with berries',
      lunch: 'Turkey wrap',
      dinner: 'Stir-fried tofu with rice',
    },
    [format(new Date(Date.now() + 2 * 86400000), 'yyyy-MM-dd')]: {
      breakfast: 'Smoothie bowl',
      lunch: 'Quinoa salad',
      dinner: 'Grilled steak with sweet potatoes',
    },
  };

  const selectedDateKey = selectedDate
    ? format(selectedDate, 'yyyy-MM-dd')
    : '';
  const dayMeals = meals[selectedDateKey] || {};

  return (
    <div className="flex min-h-screen w-full flex-col gap-4 p-4">
      <h2 className="text-4xl font-semibold">Food Planner</h2>
      <div className="flex gap-8">
        <div className="flex-1">
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={setSelectedDate}
            className="w-full"
            captionLayout="dropdown"
          />
        </div>
      </div>
      <div className="my-4 border-t border-gray-300"></div>
      <div className="mt-4">
        {selectedDate ? (
          <>
            <h3 className="mb-2 text-2xl font-semibold">
              Meals for {format(selectedDate, 'MMMM d, yyyy')}
            </h3>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div className="rounded-lg bg-cyan-100 p-4 shadow-lg">
                <h4 className="text-lg font-semibold">Breakfast</h4>
                <p className="text-gray-600">
                  {dayMeals.breakfast || 'No breakfast planned'}
                </p>
              </div>
              <div className="rounded-lg bg-teal-100 p-4 shadow-lg">
                <h4 className="text-lg font-semibold">Lunch</h4>
                <p className="text-gray-600">
                  {dayMeals.lunch || 'No lunch planned'}
                </p>
              </div>
              <div className="rounded-lg bg-blue-50 p-4 shadow-lg">
                <h4 className="text-lg font-semibold">Dinner</h4>
                <p className="text-gray-600">
                  {dayMeals.dinner || 'No dinner planned'}
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className=" flex min-h-[200px] flex-col items-center justify-center">
            <h3 className="text-foreground mb-1 text-xl font-semibold">
              Ups! No Date Selected
            </h3>
            <p className="text-muted-foreground max-w-md px-4 text-center text-sm">
              Please pick a date from the calendar to see diary.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FoodPlanner;
