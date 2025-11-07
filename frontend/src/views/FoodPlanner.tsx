import { useState } from 'react';
import { Calendar } from '../components/ui/calendar';
import { format } from 'date-fns';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';

const FoodPlanner = () => {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<Date | undefined>();

  const {
    data: meals = {},
    isLoading,
    error,
  } = useQuery({
    queryKey: ['diet-plan'],
    queryFn: async () => {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/diet/plan`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
           body: JSON.stringify({
             days: 7,
             start_date: format(new Date(), 'yyyy-MM-dd'),
             preferences: {},
           }),
        }
      );
      if (!response.ok) {
        throw new Error('Failed to fetch diet plan');
      }
      return response.json();
    },
  });

  const selectedDateKey = selectedDate
    ? format(selectedDate, 'yyyy-MM-dd')
    : '';
  const dayMeals = meals[selectedDateKey] || {};

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading diet plan</div>;

  return (
    <div className="flex min-h-screen w-full flex-col gap-4">
      <div className="grid w-full grid-cols-[40px_1fr_40px] items-center justify-center">
        <ArrowLeft onClick={() => navigate({ to: '/home' })} />
        <h1 className="text-2xl font-medium inline-flex justify-center">
          Food Planner
        </h1>
        <div></div>
      </div>
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
          <div className="flex min-h-[200px] flex-col items-center justify-center">
            <h3 className="text-foreground mb-1 text-xl font-semibold">
              Ups! No Date Selected
            </h3>
            <p className="text-muted-foreground px-4 text-center text-sm">
              Please pick a date from the calendar to see diary.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FoodPlanner;
