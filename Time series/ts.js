document.addEventListener("DOMContentLoaded", async function () {
    // Function to load CSV data
    async function loadCSV(filePath) {
        return new Promise((resolve, reject) => {
            fetch(filePath)
                .then(response => response.text())
                .then(csvData => {
                    Papa.parse(csvData, {
                        header: true,
                        skipEmptyLines: true,
                        complete: function (results) {
                            resolve(results.data);
                        }
                    });
                })
                .catch(error => reject(error));
        });
    }

    // Function to process daily time series data
    function processTimeSeries(data) {
        let timeSeries = {};

        // Loop through each row in the CSV data
        data.forEach(row => {
            // Extract the date in the format YYYY/MM/DD from the pickedUp column
            let date = row.pickedUp.split(" ")[0]; // Extract date (YYYY/MM/DD)
            let sentiment = parseFloat(row.sentiment); // Parse the sentiment score

            // If the date does not exist in the time series object, initialize it
            if (!timeSeries[date]) {
                timeSeries[date] = { sum: 0, count: 0 };
            }

            // Sum up sentiment values and count occurrences for each date
            timeSeries[date].sum += sentiment;
            timeSeries[date].count += 1;
        });

        // Prepare the processed data by calculating the average sentiment per date
        let processedData = Object.keys(timeSeries).sort().map(date => ({
            date: date,
            avgSentiment: timeSeries[date].sum / timeSeries[date].count
        }));

        return processedData;
    }

    // Function to calculate the average and standard deviation of sentiment scores
    function calculateStats(data) {
        const sentiments = data.map(d => d.avgSentiment);
        const average = sentiments.reduce((sum, val) => sum + val, 0) / sentiments.length;
        const variance = sentiments.reduce((sum, val) => sum + Math.pow(val - average, 2), 0) / sentiments.length;
        const stdDev = Math.sqrt(variance);

        return {
            average,
            stdDev,
            lowerBound: average - stdDev,
            upperBound: average + stdDev
        };
    }

    // Function to plot daily time series with bounds and average line
    function plotTimeSeries(processedData, stats) {
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: processedData.map(d => d.date),
                datasets: [
                    {
                        label: 'Average Daily Sentiment Score',
                        data: processedData.map(d => d.avgSentiment),
                        borderColor: 'blue',
                        backgroundColor: 'rgba(0, 0, 255, 0.1)',
                        fill: true
                    },
                    {
                        label: 'Upper Bound (Mean + 1 SD)',
                        data: Array(processedData.length).fill(stats.upperBound),
                        borderColor: 'red',
                        borderDash: [5, 5],
                        borderWidth: 1,
                        fill: false
                    },
                    {
                        label: 'Lower Bound (Mean - 1 SD)',
                        data: Array(processedData.length).fill(stats.lowerBound),
                        borderColor: 'green',
                        borderDash: [5, 5],
                        borderWidth: 1,
                        fill: false
                    },
                    {
                        label: 'Average Sentiment',
                        data: Array(processedData.length).fill(stats.average),
                        borderColor: 'orange',
                        borderDash: [5, 5],
                        borderWidth: 1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: 'Date' } },
                    y: { title: { display: true, text: 'Average Sentiment' } }
                },
                plugins: {
                    annotation: {
                        annotations: {
                            upperBound: {
                                type: 'line',
                                yMin: stats.upperBound,
                                yMax: stats.upperBound,
                                borderColor: 'red',
                                borderWidth: 2,
                                borderDash: [5, 5]
                            },
                            lowerBound: {
                                type: 'line',
                                yMin: stats.lowerBound,
                                yMax: stats.lowerBound,
                                borderColor: 'green',
                                borderWidth: 2,
                                borderDash: [5, 5]
                            },
                            averageLine: {
                                type: 'line',
                                yMin: stats.average,
                                yMax: stats.average,
                                borderColor: 'orange',
                                borderWidth: 2,
                                borderDash: [5, 5]
                            }
                        }
                    }
                }
            }
        });
    }

    // Load data, process, and plot
    try {
        let csvData = await loadCSV('sample1000.csv');
        let processedData = processTimeSeries(csvData);

        // Calculate statistics (average, standard deviation, bounds)
        const stats = calculateStats(processedData);
        console.log("Stats:", stats);

        // Plot the time series with bounds and average line
        plotTimeSeries(processedData, stats);
    } catch (error) {
        console.error("Error loading or processing data:", error);
    }
});