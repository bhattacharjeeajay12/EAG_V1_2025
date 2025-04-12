// Function to count vowels in a string
export function count_vowels(string) {
    return (string.match(/[aeiouAEIOU]/g) || []).length;
}

// Function to compute factorial
export function compute_factorial(n) {
    if (n === 0 || n === 1) return 1;
    return n * compute_factorial(n - 1);
}

// Function to get today's day
export function get_today_day() {
    return new Date().getDate();
}

// Function to get current hour
export function get_current_hour() {
    return new Date().getHours();
}

// Function to compute a^2 - b^3
export function compute_a_squared_minus_b_cubed(a, b) {
    return (a * a) - (b * b * b);
}

// Function to split number into digits
export function split_number_into_digits(number) {
    return String(number).split('').map(Number);
}

// Function to square numbers in a list
export function square_numbers_in_list(numbers) {
    // If numbers is already an array, use it directly
    if (Array.isArray(numbers)) {
        return numbers.map(n => {
            const num = parseFloat(n);
            if (isNaN(num)) return `Error: ${n} is not a valid number`;
            return num * num;
        });
    }

    // Try to convert string to array
    if (typeof numbers === 'string') {
        try {
            numbers = JSON.parse(numbers);
        } catch (e) {
            numbers = numbers.split(',').map(x => parseFloat(x.trim()));
        }
    } else {
        return `Error: Input must be an array or comma-separated string of numbers`;
    }

    return numbers.map(n => {
        const num = parseFloat(n);
        if (isNaN(num)) return `Error: ${n} is not a valid number`;
        return num * num;
    });
}

// Function to sum numbers in a list
export function sum_numbers_in_list(numbers) {
    // If numbers is already an array, use it directly
    if (Array.isArray(numbers)) {
        return numbers.reduce((a, b) => {
            const numA = parseFloat(a);
            const numB = parseFloat(b);
            if (isNaN(numA) || isNaN(numB)) return `Error: Invalid numbers in list`;
            return numA + numB;
        }, 0);
    }

    // Try to convert string to array
    if (typeof numbers === 'string') {
        try {
            numbers = JSON.parse(numbers);
        } catch (e) {
            numbers = numbers.split(',').map(x => parseFloat(x.trim()));
        }
    } else {
        return `Error: Input must be an array or comma-separated string of numbers`;
    }

    return numbers.reduce((a, b) => {
        const numA = parseFloat(a);
        const numB = parseFloat(b);
        if (isNaN(numA) || isNaN(numB)) return `Error: Invalid numbers in list`;
        return numA + numB;
    }, 0);
}

// Function to convert string to ASCII values
export function convert_string_to_ascii(string) {
    return string.split('').map(char => char.charCodeAt(0));
}

// Function to multiply list elements
export function multiply_list_elements(numbers) {
    // If numbers is already an array, use it directly
    if (Array.isArray(numbers)) {
        return numbers.reduce((a, b) => {
            const numA = parseFloat(a);
            const numB = parseFloat(b);
            if (isNaN(numA) || isNaN(numB)) return `Error: Invalid numbers in list`;
            return numA * numB;
        }, 1);
    }

    // Try to convert string to array
    if (typeof numbers === 'string') {
        try {
            numbers = JSON.parse(numbers);
        } catch (e) {
            numbers = numbers.split(',').map(x => parseFloat(x.trim()));
        }
    } else {
        return `Error: Input must be an array or comma-separated string of numbers`;
    }

    return numbers.reduce((a, b) => {
        const numA = parseFloat(a);
        const numB = parseFloat(b);
        if (isNaN(numA) || isNaN(numB)) return `Error: Invalid numbers in list`;
        return numA * numB;
    }, 1);
}

// Function to compute log base 2
export function compute_log2(number) {
    const num = parseFloat(number);
    if (isNaN(num)) return `Error: ${number} is not a valid number`;
    return Math.log2(num);
} 