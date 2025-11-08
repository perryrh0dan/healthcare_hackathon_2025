import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
} from "chart.js";

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale);

export default function LineChart({labels, data}: {labels: Array<string>, data: Array<number>}) {
  const chartData = {
    labels: labels,
    datasets: [
      {
        data: data,
        borderColor: "#3b82f6", // Tailwind blue-500
        borderWidth: 2,
        tension: 0.4,
        pointRadius: 0, // hide points
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
    },
    scales: {
      x: {
        display: false, // hide x-axis
        grid: { display: false, drawBorder: false },
      },
      y: {
        display: false, // hide y-axis
        grid: { display: false, drawBorder: false },
      },
    },
    elements: {
      line: {
        borderJoinStyle: "round",
      },
    },
  } as const;

  return (
    <div style={{ height: "100%" }}>
      <Line data={chartData} options={options} />
    </div>
  );
}
