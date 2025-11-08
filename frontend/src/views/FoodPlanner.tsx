import { useState } from 'react';
import { Calendar } from '../components/ui/calendar';
import { format } from 'date-fns';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';

interface CalendarEvent {
  from_timestamp: string;
  description: string;
}

const FoodPlanner = () => {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(
    new Date()
  );

  const selectedDateKey = selectedDate
    ? format(selectedDate, 'yyyy-MM-dd')
    : '';

  const { data: planEvents = [], isLoading: isPlanLoading } = useQuery<
    CalendarEvent[]
  >({
    queryKey: ['calendar-plan'],
    queryFn: async () => {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/diet/plan`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            days: 7,
            start_date: new Date(),
            preferences: {},
          }),
        }
      );
      if (!response.ok) {
        throw new Error('Failed to fetch calendar plan');
      }
      const data = await response.json();
      return data.events || [];
    },
    staleTime: Infinity,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
  });

  const { data: allEvents = [] } = useQuery<CalendarEvent[]>({
    queryKey: ['calendar'],
    queryFn: async () => {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/calendar/`,
        {
          credentials: 'include',
        }
      );
      if (!response.ok) {
        throw new Error('Failed to fetch calendar events');
      }
      const data = await response.json();
      return data.events || [];
    },
    enabled: !isPlanLoading,
  });

  const allEventDates = [...allEvents].map((e) => new Date(e.from_timestamp));
  const modifiers = { hasEvent: allEventDates };

  const eventsForDay = allEvents.filter(
    (e) => format(new Date(e.from_timestamp), 'yyyy-MM-dd') === selectedDateKey
  );

  const parsedMeals = {
    breakfast:
      eventsForDay
        .filter((e) => e.description.includes('Breakfast:'))
        .map((e) => e.description.split('Breakfast: ')[1])
        .join('<br />') || 'No breakfast planned',
    lunch:
      eventsForDay
        .filter((e) => e.description.includes('Lunch:'))
        .map((e) => e.description.split('Lunch: ')[1])
        .join('<br />') || 'No lunch planned',
    dinner:
      eventsForDay
        .filter((e) => e.description.includes('Dinner:'))
        .map((e) => e.description.split('Dinner: ')[1])
        .join('<br />') || 'No dinner planned',
    snack:
      eventsForDay
        .filter((e) => e.description.includes('Snack:'))
        .map((e) => e.description.split('Snack: ')[1])
        .join('<br />') || 'No snack planned',
  };

  if (isPlanLoading) {
    return (
      <div className="flex min-h-screen animate-pulse items-center justify-center">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen w-full flex-col gap-4">
      <div className="grid w-full grid-cols-[40px_1fr_40px] items-center justify-center">
        <ArrowLeft onClick={() => navigate({ to: '/home' })} />
        <h1 className="inline-flex justify-center text-2xl font-medium">
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
            modifiers={modifiers}
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
            <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
              <div className="rounded-lg bg-cyan-100 p-4 shadow-lg">
                <h4 className="text-lg font-semibold">Breakfast</h4>
                <p
                  className="text-gray-600"
                  dangerouslySetInnerHTML={{ __html: parsedMeals.breakfast }}
                />
              </div>
              <div className="rounded-lg bg-teal-100 p-4 shadow-lg">
                <h4 className="text-lg font-semibold">Lunch</h4>
                <p
                  className="text-gray-600"
                  dangerouslySetInnerHTML={{ __html: parsedMeals.lunch }}
                />
              </div>
              <div className="rounded-lg bg-blue-50 p-4 shadow-lg">
                <h4 className="text-lg font-semibold">Dinner</h4>
                <p
                  className="text-gray-600"
                  dangerouslySetInnerHTML={{ __html: parsedMeals.dinner }}
                />
              </div>
              <div className="rounded-lg bg-green-100 p-4 shadow-lg">
                <h4 className="text-lg font-semibold">Snack</h4>
                <p
                  className="text-gray-600"
                  dangerouslySetInnerHTML={{ __html: parsedMeals.snack }}
                />
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
