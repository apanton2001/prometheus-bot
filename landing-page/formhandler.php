<?php
// Prevent direct access to this file
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('HTTP/1.1 403 Forbidden');
    exit('Direct access to this file is forbidden.');
}

// Configuration
$recipients = ['youremail@example.com']; // Replace with your email address
$subject = 'New PrometheusAI Early Access Request';
$redirect_success = 'thank-you.html'; // Create this file to show a thank you message
$redirect_error = 'error.html'; // Create this file to show an error message

// Get form data and sanitize
$name = filter_input(INPUT_POST, 'name', FILTER_SANITIZE_STRING);
$email = filter_input(INPUT_POST, 'email', FILTER_SANITIZE_EMAIL);
$trading_experience = filter_input(INPUT_POST, 'trading-experience', FILTER_SANITIZE_STRING);
$plan = filter_input(INPUT_POST, 'plan', FILTER_SANITIZE_STRING);

// Validate data
if (empty($name) || empty($email) || empty($trading_experience) || empty($plan)) {
    redirect($redirect_error);
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    redirect($redirect_error);
}

// Store data in a CSV file (as a simple database)
$data_file = 'data/signups.csv';

// Create the data directory if it doesn't exist
if (!file_exists('data')) {
    mkdir('data', 0755, true);
}

// Prepare the data for CSV
$data = [
    date('Y-m-d H:i:s'),
    $name,
    $email,
    $trading_experience,
    $plan,
    $_SERVER['REMOTE_ADDR']
];

// Open the file for appending
$fp = fopen($data_file, 'a');

// Write the data
if ($fp) {
    // If the file is new, write the header
    if (filesize($data_file) === 0) {
        fputcsv($fp, ['Timestamp', 'Name', 'Email', 'Trading Experience', 'Plan', 'IP Address']);
    }
    
    fputcsv($fp, $data);
    fclose($fp);
}

// Prepare and send the email notification
$message = "New PrometheusAI Early Access Request\n\n";
$message .= "Name: " . $name . "\n";
$message .= "Email: " . $email . "\n";
$message .= "Trading Experience: " . $trading_experience . "\n";
$message .= "Selected Plan: " . $plan . "\n";
$message .= "IP Address: " . $_SERVER['REMOTE_ADDR'] . "\n";
$message .= "Date: " . date('Y-m-d H:i:s') . "\n";

$headers = 'From: noreply@prometheusai.com' . "\r\n" .
    'Reply-To: ' . $email . "\r\n" .
    'X-Mailer: PHP/' . phpversion();

foreach ($recipients as $recipient) {
    mail($recipient, $subject, $message, $headers);
}

// Set a cookie for returning visitors
setcookie('prometheusai_signup', '1', time() + 60*60*24*365, '/'); // 1 year

// Redirect to thank you page
redirect($redirect_success);

// Helper function for redirects
function redirect($url) {
    header('Location: ' . $url);
    exit();
}
?> 