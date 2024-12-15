import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import './App.css';

function App() {
  const [data, setData] = useState([]);
  const [playerStats, setPlayerStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetch('http://localhost:5001/api/sentiment')
      .then(response => response.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const uniquePlayers = [...new Set(data.map(item => item.player))];
    
    // Fetch player stats sequentially instead of all at once
    const fetchPlayerStats = async () => {
      for (const player of uniquePlayers) {
        try {
          const response = await fetch(`http://localhost:5001/api/player-stats/${encodeURIComponent(player)}`);
          const stats = await response.json();
          
          if (response.ok) {
            setPlayerStats(prev => ({
              ...prev,
              [player]: stats
            }));
          } else {
            setErrors(prev => ({
              ...prev,
              [player]: stats.message || 'Failed to fetch stats'
            }));
          }
        } catch (error) {
          console.error(`Error fetching stats for ${player}:`, error);
          setErrors(prev => ({
            ...prev,
            [player]: 'Failed to fetch stats'
          }));
        }
      }
    };

    if (data.length > 0) {
      fetchPlayerStats();
    }
  }, [data]);

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
      {loading ? (
        <p>Loading data...</p>
      ) : (
        <>
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
          
          <div className="player-stats-grid">
            {chartData.map(({ player }) => (
              <div key={player} className="player-card">
                <h3>{player}</h3>
                {errors[player] ? (
                  <p className="error-message">{errors[player]}</p>
                ) : playerStats[player] ? (
                  <div className="stats-content">
                    <p>Points: {playerStats[player].pts}</p>
                    <p>Rebounds: {playerStats[player].reb}</p>
                    <p>Assists: {playerStats[player].ast}</p>
                    <p>Plus/Minus: {playerStats[player].plus_minus}</p>
                    <p>Date: {playerStats[player].date}</p>
                  </div>
                ) : (
                  <p>Loading stats...</p>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default App;