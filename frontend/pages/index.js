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
    const [chosenDestination, setChosenDestination] = useState('');
    const [images, setImages] = useState([]);

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
        setLoading(true); // Indicate loading state
        setError(''); // Reset any previous errors
        setChosenDestination(destination);
        try {
                const response = await axios.get(`http://127.0.0.1:8000/chosen_destination_daily_plan`, {
                        params: { // Notice the use of 'params' to send query parameters correctly
                                destination: destination,
                                start_date: startDate,
                                end_date: endDate
                        }
                });
                //chosenDestination = destination; // Save the chosen destination for later use
                setDailyPlan(response.data.data); // Assuming the response has a 'data' property that contains the daily plan
        } catch (error) {
                console.error('Failed to fetch daily plan:', error);
                setError('Failed to fetch daily plan. Please try again.');
        }
        setLoading(false); // Reset loading state after the operation is complete
    };
    
    const handleFetchImages = async () => {
        setLoading(true);
        setError('');
        console.log('Fetching images for:', chosenDestination, 'with daily plan:', dailyPlan); // Log the chosen destination and daily plan
        try {
            const response = await axios.get(`http://127.0.0.1:8000/dalle_image`, {
                params: {
                    destination: chosenDestination,  // Make sure this variable holds the last clicked destination
                    daily_plan: dailyPlan
                }
            });
            setImages(response.data.data);
        } catch (error) {
            console.error('Failed to fetch images:', error);
            setError('Failed to fetch images. Please try again.');
        }
        setLoading(false);
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
                    {results && Object.keys(results).length > 0 ? (
                        Object.entries(results).map(([destination, details]) => (
                            <tr key={destination} onClick={() => handleDestinationClick(destination)}>
                                <td className={styles.td} style={{ cursor: 'pointer', color: '#61dafb' }}>{destination}</td>
                                <td className={styles.td}>{details.depart_airport_code} to {details.destination_airport_code}<br />
                                Direct: {details.is_direct_flight}<br />
                                Flights: {details.flight_numbers.join(', ')}<br />
                                Duration: {details.total_duration}</td>
                                <td className={styles.td}>{details.hotel_name}<br />
                                Address: {details.hotel_address}<br />
                                Rating: {details.hotel_rating}</td>
                                <td className={styles.td}>${details.remaining_budget}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="4" className={styles.td}>No results found</td>
                        </tr>
                    )}
                </tbody>


            </table>

            <div className={styles.container}>
            {dailyPlan && (
                <div className={styles.planContainer}>
                    <h2 className={styles.h2}>Daily Plan</h2>
                    <table className={styles.table}>
                        <thead>
                            <tr>
                            <th className={styles.th}>Day</th>
                            <th className={styles.th}>Activities</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dailyPlan.split('\n').map((plan, index) => (
                            <tr key={index}>
                                <td className={styles.td}>Day {index + 1}</td>
                                <td className={styles.td}>{plan.replace(`Day ${index + 1}: `, '')}</td>
                            </tr>
                            ))}
                        </tbody>
                        </table>
                    <button onClick={handleFetchImages} className={styles.button}>
                        Get DALL-E Images

                    </button>
                </div>
            )}
            {images.length > 0 && (
                <table className={styles.table}>
                    <tbody>
                        <tr>
                            <td className={styles.td}><a href={images[0]} target="_blank" rel="noopener noreferrer">Image 1</a></td>
                            <td className={styles.td}><a href={images[1]} target="_blank" rel="noopener noreferrer">Image 2</a></td>
                        </tr>
                        <tr>
                            <td className={styles.td}><a href={images[2]} target="_blank" rel="noopener noreferrer">Image 3</a></td>
                            <td className={styles.td}><a href={images[3]} target="_blank" rel="noopener noreferrer">Image 4</a></td>
                        </tr>
                    </tbody>
                </table>
            )}
            {/* Handling errors and loading state */}
            {error && <p className={styles.error}>{error}</p>}
            {loading && <p>Loading...</p>}
        </div>
        </div> // Add closing </div> tag here
    );
}