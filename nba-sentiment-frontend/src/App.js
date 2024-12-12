import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import './App.css';

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5001/api/sentiment')
      .then(response => response.json())
      .then(data => setData(data))
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  // Group data by player and calculate average sentiment
  const groupedData = data.reduce((acc, item) => {
    if (!acc[item.player]) {
      acc[item.player] = { player: item.player, sentiment: 0, count: 0 };
    }
    acc[item.player].sentiment += item.sentiment;
    acc[item.player].count += 1;
    return acc;
  }, {});

  const chartData = Object.values(groupedData)
    .map(item => ({
      player: item.player,
      sentiment: (item.sentiment / item.count).toFixed(2),
    }))
    .sort((a, b) => b.sentiment - a.sentiment); // Sort by sentiment descending

  // Custom tick component to ensure names are on one line
  const renderCustomYAxisTick = ({ x, y, payload }) => {
    return (
      <text x={x} y={y} dy={4} textAnchor="end" fill="#666" transform={`rotate(0, ${x}, ${y})`}>
        {payload.value}
      </text>
    );
  };

  return (
    <div className="App">
      <h1>NBA Sentiment Analysis</h1>
      {chartData.length > 0 ? (
        <div className="chart-container">
          <BarChart
            width={1200}
            height={800}
            data={chartData}
            layout="vertical"
            margin={{ top: 20, right: 50, left: 150, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[-1, 1]} />
            <YAxis 
              dataKey="player" 
              type="category" 
              tick={renderCustomYAxisTick} // Use custom tick renderer
              interval={0}
            />
            <Tooltip />
            <Legend />
            <Bar dataKey="sentiment" fill="#8884d8" />
          </BarChart>
        </div>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}

export default App;