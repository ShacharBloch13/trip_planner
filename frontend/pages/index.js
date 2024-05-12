import { useState } from 'react';
import axios from 'axios';
//import styles from '../styles/Home.module.css';

export default function Home() {
    const [formData, setFormData] = useState({
        start_date: '',
        end_date: '',
        budget: '',
        trip_type: ''
    });
    const [destination, setDestination] = useState('');
    const [showImages, setShowImages] = useState(false);
    const [results, setResults] = useState(null);
    const [dailyPlan, setDailyPlan] = useState('');
    const [imageLinks, setImageLinks] = useState([]);

    const handleInput = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const searchOptions = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/search_options', { params: formData }); // change to localhost if running locally
            console.log('Making request to:', `http://localhost:8000/search_options`);

            setResults(response.data.data);
        } catch (error) {
            console.error('Error fetching travel options:', error);
        }
    };

    const fetchDailyPlan = async () => {
        try {
            const response = await axios.get(`http://127.0.0.1:8000/chosen_destination_daily_plan`, {
                params: { destination: destination, start_date: formData.start_date, end_date: formData.end_date }
            });
            setDailyPlan(response.data.data);
        } catch (error) {
            console.error('Error fetching daily plan:', error);
        }
    };

    const fetchImages = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/dalle_image', {
                params: { destination: destination, daily_plan: dailyPlan }
            });
            setImageLinks(response.data.data);
        } catch (error) {
            console.error('Error fetching images:', error);
        }
    };

    return (
        <div>
            <div>
                <input type="text" name="start_date" value={formData.start_date} onChange={handleInput} placeholder="Start Date (YYYY-MM-DD)" />
                <input type="text" name="end_date" value={formData.end_date} onChange={handleInput} placeholder="End Date (YYYY-MM-DD)" />
                <input type="text" name="budget" value={formData.budget} onChange={handleInput} placeholder="Budget" />
                <input type="text" name="trip_type" value={formData.trip_type} onChange={handleInput} placeholder="Trip Type (e.g., beach, adventure)" />
                <button onClick={searchOptions}>Search Travel Options</button>
            </div>
            {results && (
                <div>
                    <select onChange={(e) => setDestination(e.target.value)}>
                        {results.map((option, index) => (
                            <option key={index} value={option.destination}>{option.destination}</option>
                        ))}
                    </select>
                    <button onClick={fetchDailyPlan}>Get Daily Plan</button>
                </div>
            )}
            {dailyPlan && (
                <div>
                    <p>{dailyPlan}</p>
                    <button onClick={() => setShowImages(true)}>Show Images</button>
                </div>
            )}
            {showImages && (
                <div>
                    {imageLinks.map((link, index) => (
                        <a key={index} href={link} target="_blank" rel="noopener noreferrer">View Image {index + 1}</a>
                    ))}
                </div>
            )}
        </div>
    );
}
