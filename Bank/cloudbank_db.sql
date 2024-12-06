-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 22, 2024 at 04:48 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cloudbank_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `account_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `account_type` enum('Savings','Business') NOT NULL,
  `balance` decimal(15,2) DEFAULT 0.00,
  `account_status` enum('Active','Closed','Frozen') DEFAULT 'Active',
  `opened_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `full_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`account_id`, `user_id`, `account_type`, `balance`, `account_status`, `opened_at`, `full_name`) VALUES
(1, 3, 'Savings', 2400.00, 'Active', '2024-10-16 05:54:52', 'Ravi'),
(2, 4, 'Savings', 600.00, 'Active', '2024-10-16 05:55:59', 'Shankar');

-- --------------------------------------------------------

--
-- Table structure for table `account_statements`
--

CREATE TABLE `account_statements` (
  `statement_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `transaction_type` enum('Credit','Debit') NOT NULL,
  `transaction_amount` decimal(15,2) NOT NULL,
  `transaction_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `description` text DEFAULT NULL,
  `from_account_id` int(11) DEFAULT NULL,
  `to_account_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_statements`
--

INSERT INTO `account_statements` (`statement_id`, `user_id`, `transaction_type`, `transaction_amount`, `transaction_date`, `description`, `from_account_id`, `to_account_id`) VALUES
(1, 3, '', 1000.00, '2024-10-16 06:25:04', 'Deposit', 1, NULL),
(2, 3, '', 1000.00, '2024-10-16 07:10:08', 'Deposit', 1, NULL),
(3, 3, '', 100.00, '2024-10-16 07:15:38', 'Transfer to Shankar', 1, 2);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `phone` varchar(10) NOT NULL,
  `address` text DEFAULT NULL,
  `aadhar_number` char(12) NOT NULL,
  `pan_card` char(10) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `full_name`, `email`, `password`, `phone`, `address`, `aadhar_number`, `pan_card`, `created_at`) VALUES
(3, 'Ravi', 'rajubye189@gmail.com', 'raju@123', '9876543219', 'mit campus,anna university,chromepet,chennai', '123412341234', 'ABC1234567', '2024-10-16 05:54:52'),
(4, 'Shankar', 'ravishankarmitit@gmail.com', 'Ravi@123', '6381649403', 'nehru nagar,Chromepet,chennai-600064', '432143214321', 'BAC1231231', '2024-10-16 05:55:59');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`account_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `account_statements`
--
ALTER TABLE `account_statements`
  ADD PRIMARY KEY (`statement_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `from_account_id` (`from_account_id`),
  ADD KEY `to_account_id` (`to_account_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `account_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `account_statements`
--
ALTER TABLE `account_statements`
  MODIFY `statement_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `account_statements`
--
ALTER TABLE `account_statements`
  ADD CONSTRAINT `account_statements_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  ADD CONSTRAINT `account_statements_ibfk_2` FOREIGN KEY (`from_account_id`) REFERENCES `accounts` (`account_id`),
  ADD CONSTRAINT `account_statements_ibfk_3` FOREIGN KEY (`to_account_id`) REFERENCES `accounts` (`account_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
