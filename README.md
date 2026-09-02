# Yellow Pages Business Intelligence Platform

## Overview

The Yellow Pages Business Intelligence Platform is a cloud-native data acquisition and management system designed to automate the collection, storage, management, and deployment of business directory data.

The project began as a large-scale web scraping solution for extracting business information from online directories. It evolved into a complete business intelligence platform that allows users to search, manage, update, export, and maintain business records through a web-based dashboard.

The platform is fully containerized using Docker, deployed on AWS EC2, connected to MongoDB Atlas, and automated through GitHub Actions CI/CD pipelines.

---

## Project Journey

This project was developed end-to-end, covering the complete software lifecycle:

1. Automated Yellow Pages data extraction using Python.
2. Data cleaning and transformation.
3. Storage of structured business data in MongoDB Atlas.
4. Development of a FastAPI-based administration dashboard.
5. Implementation of search, filtering, update, delete, and export functionality.
6. Separation of scraping and application workloads across different environments.
7. Containerization using Docker.
8. Deployment to AWS EC2.
9. Reverse proxy configuration using Nginx.
10. CI/CD automation using GitHub Actions.

The result is a production-style cloud-native business intelligence platform that demonstrates Data Engineering, Backend Development, Cloud Deployment, and DevOps practices.

---

## Key Features

### Data Acquisition

* Automated business directory scraping
* Multi-page data collection
* Structured JSON and CSV output generation
* Scalable data ingestion workflow

### Data Management

* Business record search and filtering
* Record editing and updating
* Record deletion
* Centralized business data management

### Data Export

* CSV export
* Excel export
* Custom dataset extraction

### Cloud Infrastructure

* MongoDB Atlas cloud database
* AWS EC2 deployment
* Docker containerization
* Nginx reverse proxy
* GitHub Actions CI/CD

---

## Technology Stack

### Backend

* Python
* FastAPI
* Jinja2

### Database

* MongoDB Atlas
* PyMongo

### Data Processing

* Pandas
* OpenPyXL

### DevOps & Cloud

* Docker
* Nginx
* AWS EC2
* GitHub Actions
* Linux (Ubuntu)

### Version Control

* Git
* GitHub

---

## System Architecture

GitHub Repository
↓
GitHub Actions CI/CD
↓
AWS EC2
↓
Docker Container
↓
FastAPI Dashboard
↓
MongoDB Atlas

Data Scraper
↓
Business Data Collection
↓
MongoDB Atlas
↓
Dashboard Access Layer

---

## CI/CD Workflow

Every code push to the main branch automatically:

1. Triggers GitHub Actions.
2. Connects securely to AWS EC2 through SSH.
3. Pulls the latest source code.
4. Rebuilds the Docker image.
5. Restarts the application container.
6. Deploys the updated application.

This eliminates manual deployment steps and enables automated delivery.

---

## DevOps Highlights

* Containerized application deployment using Docker.
* Reverse proxy implementation using Nginx.
* Cloud deployment on AWS EC2.
* Automated CI/CD pipelines using GitHub Actions.
* Secure environment configuration using GitHub Secrets.
* MongoDB Atlas cloud database integration.

---

## Business Value

This platform transforms raw business directory data into a centralized and manageable business intelligence system, enabling efficient data collection, maintenance, and export workflows while demonstrating modern cloud-native deployment practices.

---

## Future Enhancements

* Docker Compose orchestration
* HTTPS/SSL using Let's Encrypt
* Custom domain integration
* Monitoring with Grafana and Prometheus
* Infrastructure as Code using Terraform
* Docker Registry integration (Docker Hub / Amazon ECR)

