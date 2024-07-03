# Technical Specification

### Table of Contents
- [Technical Specification](#technical-specification)
    - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
    - [1.1 Project Overview](#11-project-overview)
    - [1.2 Document Purpose](#12-document-purpose)
    - [1.3 Intended Audience](#13-intended-audience)
    - [1.4 Scope](#14-scope)
  - [2. System Architecture](#2-system-architecture)
    - [2.1 Overview](#21-overview)
    - [2.2 System Architecture Diagram](#22-system-architecture-diagram)
  - [3. AI Model](#3-ai-model)
    - [3.1 Model Development](#31-model-development)
      - [➭ 3.1.1 Data Collection](#-311-data-collection)
      - [➭ 3.1.2 Data Augmentation](#-312-data-augmentation)
      - [➭ 3.1.3 Data Splitting](#-313-data-splitting)
      - [➭ 3.1.3 Data Preprocessing](#-313-data-preprocessing)
      - [➭ 3.1.4 Model Architecture](#-314-model-architecture)
      - [➭ 3.1.5 Training and Validation](#-315-training-and-validation)
      - [➭ 3.1.6 Model Evaluation](#-316-model-evaluation)
    - [3.2 Model Deployment and Usage](#32-model-deployment-and-usage)
      - [➭ 3.2.1 Model Integration](#-321-model-integration)
      - [➭ 3.2.2 Video Preprocessing for Inference](#-322-video-preprocessing-for-inference)
      - [➭ 3.2.3 Inference Process](#-323-inference-process)
      - [➭ 3.2.4 Feedback Generation](#-324-feedback-generation)
      - [➭ 3.2.5 Continuous Learning](#-325-continuous-learning)

---

## 1. Introduction

### 1.1 Project Overview
**Project Name:**
LiftGuard

**Document Title:**
Technical Specification

**Version:**
0.1

**Date:**
July 01, 2024

**Author(s):**
- Quentin CLÉMENT (Project Owner)

---

### 1.2 Document Purpose
This document outlines the technical specifications for the LiftGuard project. It serves as a guide for the development team to understand the technical details, architecture, and implementation plans required to build and maintain the application.

---

### 1.3 Intended Audience
This document is intended for software architects, developers, and testers involved in the LiftGuard project. It provides the necessary technical details to ensure a coherent and efficient development process.

---

### 1.4 Scope
The scope of this document includes detailed technical specifications for the LiftGuard mobile application, server-side application, database, and AI model. It covers the architecture, design, deployment, and testing aspects of the project.

---

## 2. System Architecture

### 2.1 Overview

The LiftGuard system is composed of the following components:

| Component | Description | Technology |
| --- | --- | --- |
| Mobile Application (Frontend) | User interface for interacting with the system | Flutter 3.22.0 |
| Mobile Application (Backend) | Server-side application handling business logic and data processing | Flutter 3.22.0 |
| Database | Storage for user data, video metadata, feedback data, and community data | Firebase |
| AI Model | Video inference engine for analyzing video content | Python 3.10.12 & TensorFlow 2.15.0 |

---

### 2.2 System Architecture Diagram

```mermaid
flowchart TD
    subgraph Mobile_Application
        direction TB
        A1[User Interface]
        A2[Client Logic]
        A3[Local Storage]
        A4[Notification Service]
    end

    subgraph Backend
        direction TB
        B1[API Gateway]
        B2[Authentication Service]
        B3[Video Processing Service]
        B4[Feedback Service]
        B5[Notification Service]
    end

    subgraph Database
        direction TB
        C1[User Data]
        C2[Video Metadata]
        C3[Feedback Data]
        C4[Community Data]
    end

    subgraph AI_Model
        direction TB
        D1[Video Inference Engine]
        D2[Model Training Component]
    end

    A2 -->|API Calls| B1
    B1 -->|Database Queries| C1
    B1 -->|Database Queries| C2
    B1 -->|Database Queries| C3
    B1 -->|Database Queries| C4
    B3 -->|gRPC Calls| D1
    D1 -->|Analysis Results| B4

    A1 -->|User Input| A2
    A2 -->|Store Data| A3
    A3 -->|Send Data| B1
    B1 -->|Route Request| B2
    B2 -->|Validate User| C1
    B2 -->|Process Video| B3
    B3 -->|Store Metadata| C2
    B3 -->|Request Analysis| D1
    D1 -->|Provide Feedback| B4
    B4 -->|Store Feedback| C3
    B4 -->|Send Feedback| A2
    B5 -->|Notify User| A4
    A4 -->|Display Notification| A1
```

---

## 3. AI Model

### 3.1 Model Development
This section covers everything related to the development and training of the AI model before it is deployed. It includes details on data collection, preprocessing, training, and validation.

#### ➭ 3.1.1 Data Collection
Creating a comprehensive dataset is crucial but challenging. Developing a dataset with a diverse range of individuals, varying body types, and different equipment is time-consuming and costly. Given the number of specific errors we aim to detect, there are no existing datasets that fully meet our requirements.

Due to time and budget constraints, a compromise is necessary. Therefore, we will create a dataset featuring three different individuals, with each person recording five videos for each following case:
- ✅ Correct
- ❌ Knee Cave (Valgus Collapse)
- ❌ Heels Lifting
- ❌ Depth

To maximize the diversity of the dataset, each video will be recorded under varying conditions:
- Different video lengths (ranging from 2 to 10 seconds)
- Different cameras (each individual will use a different smartphone with different camera specifications)
- Different angles (all within the optimal green area of the image below)
- Various lighting conditions (to simulate different environments, such as bright daylight, indoor lighting, and low light)
- Different clothing and footwear (to account for variations in attire and equipment)
- Background variability (recording in different locations to include various backgrounds and potential obstructions)
- Different exercise speeds (to account for variations in the speed of performing the squats)

<img src="./images/angle.png" height="200">

The objective is to reproduce as many real-world scenarios as possible to ensure the AI model can generalize well to diverse situations encountered in production.

#### ➭ 3.1.2 Data Augmentation
Because we can't afford to record an infinite number of videos, we will use data augmentation techniques to artificially increase the size of our dataset and simulate variations in the input data. The following data augmentation techniques will be applied:
- **Flipping**: Horizontally flip the video frames to simulate the mirror image of the squat.
  - **Multiplication Factor:** 1 time per video (flipping once doubles the dataset).
- **Adjusting Brightness**: Randomly adjust the brightness of the video frames to account for different lighting conditions.
  - **Multiplication Factor:** 2 times per video (adjusting brightness to lower and higher levels).
- **Color Jittering**: Randomly adjust the color of the video frames to simulate variations in the camera settings.
  - **Multiplication Factor:** 2 times per video (adjusting colors to create different hues and saturations).
- **Gaussian Noise**: Add Gaussian noise to the video frames to simulate noise in the input data.
  - **Multiplication Factor:** 2 times per video (adding noise at two different intensities).
- **Salt and Pepper Noise**: Add salt and pepper noise to the video frames to simulate noise in the input data.
  - **Multiplication Factor:** 2 times per video (adding noise at two different intensities).

Using these techniques, each original video can be augmented up to 16 times, significantly expanding the dataset while maintaining realistic variations.

#### ➭ 3.1.3 Data Splitting

- Training Set:
  - Ratio: 80% of the dataset
  - Number of Videos: 768 videos
  - Videos per Label: 192 videos per label

- Validation Set:
  - Ratio: 10% of the dataset
  - Number of Videos: 96 videos
  - Videos per Label: 24 videos per label

- Testing Set:
  - Ratio: 10% of the dataset
  - Number of Videos: 96 videos
  - Videos per Label: 24 videos per label

#### ➭ 3.1.3 Data Preprocessing
- **Frame Extraction:** Detail the process of extracting frames from the videos, including frame rate and resolution settings.
- **Normalization:** Describe how video frames are normalized or standardized to ensure consistent input to the model.
- **Label Encoding:** Explain the encoding of labels for different types of errors (e.g., knee cave, forward lean).

#### ➭ 3.1.4 Model Architecture
- **Neural Network Design:** Outline the architecture of the neural network used, including the types of layers (e.g., convolutional layers, pooling layers) and their configurations.
- **Hyperparameters:** Detail the key hyperparameters used during training, such as learning rate, batch size, and number of epochs.

#### ➭ 3.1.5 Training and Validation
- **Training Process:** Explain the training process, including the loss function, optimization algorithm, and any regularization techniques used.
- **Validation:** Describe how the model is validated, including the use of validation datasets and performance metrics (e.g., accuracy, precision, recall).

#### ➭ 3.1.6 Model Evaluation
- **Performance Metrics:** Provide details on the performance metrics used to evaluate the model’s accuracy and reliability.
- **Cross-Validation:** Explain any cross-validation techniques used to ensure the model's generalizability.
- **Final Model Selection:** Describe the criteria for selecting the final model for deployment.

---

### 3.2 Model Deployment and Usage
This section covers how the trained AI model is integrated into the application, including preprocessing user-uploaded videos, running inference, and generating feedback.

#### ➭ 3.2.1 Model Integration
- **Deployment Environment:** Describe the environment in which the model is deployed, including the use of TensorFlow Serving or other deployment frameworks.
- **API Integration:** Explain how the model is integrated with the backend API to handle video analysis requests.

#### ➭ 3.2.2 Video Preprocessing for Inference
- **User Video Upload:** Detail the process of handling video uploads from users, including file format and size limitations.
- **Frame Extraction:** Explain how frames are extracted from user-uploaded videos for analysis.
- **Normalization:** Describe the normalization process applied to these frames to ensure consistency with the training data.

#### ➭ 3.2.3 Inference Process
- **Inference Request:** Detail how the backend sends frames to the model for inference using gRPC or REST APIs.
- **Real-Time Processing:** Explain any real-time processing capabilities, such as how quickly the model processes frames and returns results.

#### ➭ 3.2.4 Feedback Generation
- **Output Interpretation:** Describe how the model's output is interpreted to generate user-friendly feedback, including the types of errors detected and confidence scores.
- **Feedback Presentation:** Explain how feedback is presented to the user within the mobile application, including any visualization tools used.

#### ➭ 3.2.5 Continuous Learning
- **Model Retraining:** Detail the process for continuously improving the model by retraining it with new data, including how new labeled data is collected and integrated.
- **User Feedback Loop:** Explain how user feedback is incorporated into the model improvement process.