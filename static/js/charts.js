/**
 * Fintelligence - Chart Utilities
 * 
 * This file contains utility functions for creating various types of charts
 * used throughout the financial reporting application.
 */

/**
 * Create a line chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for the X axis
 * @param {Array} datasets - Array of datasets for the chart
 * @param {string} title - Chart title
 * @param {boolean} currency - Whether to format Y axis as currency
 * @returns {Chart} The created Chart instance
 */
function drawLineChart(canvasId, labels, datasets, title, currency = false) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (currency) {
                            label += '$' + context.parsed.y.toLocaleString();
                        } else {
                            label += context.parsed.y.toLocaleString();
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                ticks: {
                    callback: function(value) {
                        if (currency) {
                            return '$' + value.toLocaleString();
                        }
                        return value.toLocaleString();
                    }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a bar chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for the X axis
 * @param {Array} datasets - Array of datasets for the chart
 * @param {string} title - Chart title
 * @param {boolean} currency - Whether to format Y axis as currency
 * @returns {Chart} The created Chart instance
 */
function drawBarChart(canvasId, labels, datasets, title, currency = false) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (currency) {
                            label += '$' + context.parsed.y.toLocaleString();
                        } else {
                            label += context.parsed.y.toLocaleString();
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                ticks: {
                    callback: function(value) {
                        if (currency) {
                            return '$' + value.toLocaleString();
                        }
                        return value.toLocaleString();
                    }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a pie chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for slices
 * @param {Array} values - Array of values for slices
 * @param {string} title - Chart title
 * @param {Array} colors - Optional array of background colors
 * @returns {Chart} The created Chart instance
 */
function drawPieChart(canvasId, labels, values, title, colors = null) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default colors if none provided
    const defaultColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)',
        'rgba(94, 212, 175, 0.7)',
        'rgba(255, 99, 12, 0.7)',
        'rgba(75, 12, 192, 0.7)'
    ];
    
    // Use provided colors or default colors
    const backgroundColors = colors || defaultColors;
    
    // Create corresponding border colors (slightly darker)
    const borderColors = backgroundColors.map(color => {
        return color.replace('0.7', '1');
    });
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = Math.round((value / total) * 100);
                        return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                    }
                }
            },
            legend: {
                position: 'right'
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors.slice(0, values.length),
                borderColor: borderColors.slice(0, values.length),
                borderWidth: 1
            }]
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a doughnut chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for slices
 * @param {Array} values - Array of values for slices
 * @param {string} title - Chart title
 * @param {Array} colors - Optional array of background colors
 * @returns {Chart} The created Chart instance
 */
function drawDoughnutChart(canvasId, labels, values, title, colors = null) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default colors if none provided
    const defaultColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)',
        'rgba(94, 212, 175, 0.7)',
        'rgba(255, 99, 12, 0.7)',
        'rgba(75, 12, 192, 0.7)'
    ];
    
    // Use provided colors or default colors
    const backgroundColors = colors || defaultColors;
    
    // Create corresponding border colors (slightly darker)
    const borderColors = backgroundColors.map(color => {
        return color.replace('0.7', '1');
    });
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = Math.round((value / total) * 100);
                        return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                    }
                }
            },
            legend: {
                position: 'right'
            }
        },
        cutout: '50%'
    };
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors.slice(0, values.length),
                borderColor: borderColors.slice(0, values.length),
                borderWidth: 1
            }]
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a radar chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for radar points
 * @param {Array} values - Array of values for radar points
 * @param {string} title - Chart title
 * @returns {Chart} The created Chart instance
 */
function drawRadarChart(canvasId, labels, values, title) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            legend: {
                display: false
            }
        },
        scales: {
            r: {
                beginAtZero: true,
                pointLabels: {
                    font: {
                        size: 12
                    }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Financial Ratios',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
            }]
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a horizontal bar chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for the Y axis
 * @param {Array} datasets - Array of datasets for the chart
 * @param {string} title - Chart title
 * @param {boolean} currency - Whether to format X axis as currency
 * @returns {Chart} The created Chart instance
 */
function drawHorizontalBarChart(canvasId, labels, datasets, title, currency = false) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const options = {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (currency) {
                            label += '$' + context.parsed.x.toLocaleString();
                        } else {
                            label += context.parsed.x.toLocaleString();
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        if (currency) {
                            return '$' + value.toLocaleString();
                        }
                        return value.toLocaleString();
                    }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a stacked bar chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for the X axis
 * @param {Array} datasets - Array of datasets for the chart
 * @param {string} title - Chart title
 * @param {boolean} currency - Whether to format Y axis as currency
 * @returns {Chart} The created Chart instance
 */
function drawStackedBarChart(canvasId, labels, datasets, title, currency = false) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (currency) {
                            label += '$' + context.parsed.y.toLocaleString();
                        } else {
                            label += context.parsed.y.toLocaleString();
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            x: {
                stacked: true
            },
            y: {
                stacked: true,
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        if (currency) {
                            return '$' + value.toLocaleString();
                        }
                        return value.toLocaleString();
                    }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a bubble chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} datasets - Array of datasets for the chart
 * @param {string} title - Chart title
 * @param {boolean} currencyX - Whether to format X axis as currency
 * @param {boolean} currencyY - Whether to format Y axis as currency
 * @returns {Chart} The created Chart instance
 */
function drawBubbleChart(canvasId, datasets, title, currencyX = false, currencyY = false) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        let xDisplay = currencyX ? '$' + context.parsed.x.toLocaleString() : context.parsed.x.toLocaleString();
                        let yDisplay = currencyY ? '$' + context.parsed.y.toLocaleString() : context.parsed.y.toLocaleString();
                        let rDisplay = context.parsed.r.toLocaleString();
                        
                        return label + `(${xDisplay}, ${yDisplay}, Size: ${rDisplay})`;
                    }
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    callback: function(value) {
                        if (currencyX) {
                            return '$' + value.toLocaleString();
                        }
                        return value.toLocaleString();
                    }
                }
            },
            y: {
                ticks: {
                    callback: function(value) {
                        if (currencyY) {
                            return '$' + value.toLocaleString();
                        }
                        return value.toLocaleString();
                    }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'bubble',
        data: {
            datasets: datasets
        },
        options: options
    });
    
    return chart;
}

/**
 * Create a polar area chart
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} labels - Array of labels for slices
 * @param {Array} values - Array of values for slices
 * @param {string} title - Chart title
 * @param {Array} colors - Optional array of background colors
 * @returns {Chart} The created Chart instance
 */
function drawPolarAreaChart(canvasId, labels, values, title, colors = null) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default colors if none provided
    const defaultColors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)',
        'rgba(94, 212, 175, 0.7)',
        'rgba(255, 99, 12, 0.7)',
        'rgba(75, 12, 192, 0.7)'
    ];
    
    // Use provided colors or default colors
    const backgroundColors = colors || defaultColors;
    
    // Create corresponding border colors (slightly darker)
    const borderColors = backgroundColors.map(color => {
        return color.replace('0.7', '1');
    });
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.label || '';
                        if (label) {
                            label += ': ';
                        }
                        label += context.formattedValue;
                        return label;
                    }
                }
            },
            legend: {
                position: 'right'
            }
        },
        scales: {
            r: {
                beginAtZero: true
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: backgroundColors.slice(0, values.length),
                borderColor: borderColors.slice(0, values.length),
                borderWidth: 1
            }]
        },
        options: options
    });
    
    return chart;
}

/**
 * Helper function to generate random colors for charts
 * 
 * @param {number} count - Number of colors to generate
 * @param {number} opacity - Opacity value (0-1)
 * @returns {Array} Array of RGBA color strings
 */
function generateRandomColors(count, opacity = 0.7) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const r = Math.floor(Math.random() * 256);
        const g = Math.floor(Math.random() * 256);
        const b = Math.floor(Math.random() * 256);
        colors.push(`rgba(${r}, ${g}, ${b}, ${opacity})`);
    }
    return colors;
}

/**
 * Create a financial comparison chart (for quarterly data)
 * 
 * @param {string} canvasId - The ID of the canvas element
 * @param {Array} periods - Array of period labels (quarters, years)
 * @param {Array} metrics - Array of metric objects with values for each period
 * @param {string} title - Chart title
 * @param {boolean} currency - Whether to format Y axis as currency
 * @returns {Chart} The created Chart instance
 */
function drawFinancialComparisonChart(canvasId, periods, metrics, title, currency = true) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const datasets = [];
    const colors = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)',
        'rgba(201, 203, 207, 0.7)',
        'rgba(94, 212, 175, 0.7)'
    ];
    
    // Create datasets from metrics
    metrics.forEach((metric, index) => {
        datasets.push({
            label: metric.name,
            data: metric.values,
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length].replace('0.7', '1'),
            borderWidth: 2
        });
    });
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title || '',
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (currency) {
                            label += '$' + context.parsed.y.toLocaleString();
                        } else {
                            label += context.parsed.y.toLocaleString();
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: false,
                ticks: {
                    callback: function(value) {
                        if (currency) {
                            return '$' + value.toLocaleString();
                        }
                        return value.toLocaleString();
                    }
                }
            }
        }
    };
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: periods,
            datasets: datasets
        },
        options: options
    });
    
    return chart;
}
