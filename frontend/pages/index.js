import { useState } from 'react';
import axios from 'axios';
import styles from '../styles/Table.module.css';

export default function Home() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [budget, setBudget] = useState('');
  const [tripType, setTripType] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});
  const [error, setError] = useState('');
  const [dailyPlan, setDailyPlan] = useState('');

  const handleSearch = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`http://127.0.0.1:8000/search_options`, {
        params: { start_date: startDate, end_date: endDate, budget, trip_type: tripType }
      });
      setResults(response.data.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setError('Failed to fetch data. Please try again.');
    }
    setLoading(false);
  };

  const handleDestinationClick = async (destination) => {
    try {
      const response = await axios.post(`http://127.0.0.1:8000/chosen_destination_daily_plan`, {
        destination,
        start_date: startDate,
        end_date: endDate
      });
      setDailyPlan(response.data.data);
    } catch (error) {
      console.error('Failed to fetch daily plan:', error);
      setError('Failed to fetch daily plan. Please try again.');
      setResults({});
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.h1}>Plan Your Trip</h1>
      <form onSubmit={handleSearch} className={styles.form}>
        <input
          className={styles.input}
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          required
        />
        <input
          className={styles.input}
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          required
        />
        <input
          className={styles.input}
          type="number"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          placeholder="Budget in USD"
          required
        />
        <input
          className={styles.input}
          type="text"
          value={tripType}
          onChange={(e) => setTripType(e.target.value)}
          placeholder="Trip Type"
          required
        />
        <button type="submit" disabled={loading} className={styles.button}>
          {loading ? 'Loading...' : 'Search'}
        </button>
      </form>

      {error && <p className={styles.text}>{error}</p>}

      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.th}>Destination</th>
            <th className={styles.th}>Flight Info</th>
            <th className={styles.th}>Hotel Info</th>
            <th className={styles.th}>Remaining Budget</th>
          </tr>
        </thead>
        <tbody>
        {results && Object.keys(results).length > 0 ?
            Object.entries(results).map(([destination, details]) => (
            <tr key={destination} onClick={() => handleDestinationClick(destination)}>
                <td className={styles.td}>{destination}</td>
                <td className={styles.td}>
                {details.depart_airport_code} to {details.destination_airport_code}<br />
                Direct: {details.is_direct_flight}<br />
                Flights: {details.flight_numbers.join(', ')}<br />
                Duration: {details.total_duration}
                </td>
                <td className={styles.td}>
                {details.hotel_name}<br />
                Address: {details.hotel_address}<br />
                Rating: {details.hotel_rating}
                </td>
                <td className={styles.td}>${details.remaining_budget}</td>
            </tr>
            )) :
            <tr>
            <td colSpan="4" className={styles.td}>No results found</td>
            </tr>
        }
        </tbody>

      </table>

      {dailyPlan && (
        <div className={styles.planContainer}>
          <h2 className={styles.h2}>Daily Plan</h2>
          <p className={styles.text}>{dailyPlan}</p>
        </div>
      )}
    </div>
  );
}
