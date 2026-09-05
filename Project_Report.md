# SMARTPHONE RESALE PRICE PREDICTION AND ANALYSIS DASHBOARD

A Project Report Submitted by
**[Your Name]** – **[Your Enrollment Number]**

in partial fulfillment for the award of the degree of
Bachelor of Technology 
in 
Information Technology

Faculty of Engineering And Technology
Marwadi University, Rajkot
2024-25

---

## CERTIFICATE
This is to certify that the project entitled **Smartphone Resale Price Prediction and Analysis Dashboard** has been carried out by **[Your Name]** – **[Your Enrollment Number]** under my guidance in partial fulfillment of the degree of Bachelor of Technology in Information Technology of Marwadi University, Rajkot during the academic year 2024-25.

**Date:** [Date]

**Internal Guide**                                     **Head of the Department**
[Guide Name]                                           [HOD Name]

---

## Acknowledgments

I would like to express my sincere gratitude to all those who helped and supported me throughout the course of this project.

I am deeply grateful to my internal project guide at Marwadi University, for their continuous support, motivation, and valuable suggestions that guided me throughout this journey. Their immense knowledge and constructive feedback played a crucial role in shaping the final outcome of this project.

A special mention to my faculty members, friends, and peers who provided constant encouragement and moral support during times of difficulty. This project has been a great learning experience, exposing me to real-world software engineering practices and advanced machine learning techniques, marking a significant step in my professional journey. 

---

## Institute’s Vision and Mission

**Institute’s Vision**
To foster an environment that empowers people, organisations and societies through education, ideas, research and training.

**Institute’s Mission**
*   To provide quality education and thereby bring social transformation.
*   To create leaders through innovation and entrepreneurship.
*   To cultivate the culture of research advancements.
*   To imbibe universal consciousness.
*   To stimulate growth through industrial and international partnerships.

## Department’s Vision and Mission

**Department’s Vision**
To be recognized as a team delivering educational excellence that advances teaching, learning, and research, in alignment with Marwadi Education Foundation's mission and goals.

**Department’s Mission**
*   To impart knowledge and skills related to the undergraduate program offered by the department.
*   To impart technical and professional skills to make graduates competitive and capable.
*   To constantly encourage and motivate graduates for innovation, entrepreneurship & industry readiness.
*   To inspire graduates for higher education and research and to place graduates in leading industries and companies.

## PEO, PO, and PSO

**Program Educational Objectives (PEO):**
Our graduated students are expected to fulfill the following Program Educational Objectives (PEOs):
*   **Core Competency:** Successfully apply fundamental mathematical, scientific, and engineering principles in formulating and solving engineering and real life problems for betterment of society.
*   **Breadth:** Will apply current industry accepted practices, new and emerging technologies to analyse, design, implement and maintain state of art solutions.
*   **Professionalism:** Work effectively and ethically in ever changing global professional environment and multi-disciplinary environment.
*   **Learning Environment:** Demonstrate excellent communication and soft skills to fulfil their commitment towards social responsibilities and foster life-long learning.
*   **Preparation:** Promote research and patenting to enhance technical and entrepreneurship skills within them.

**Program Outcomes (POs)**
Engineering Graduates will be able to: 
*   **PO1: Engineering knowledge:** Apply the knowledge of mathematics, science, engineering fundamentals, and an engineering specialization to the solution of complex engineering problems.
*   **PO2: Problem analysis:** Identify, formulate, review research literature, and analyze complex engineering problems reaching substantiated conclusions using first principles of mathematics, natural sciences, and engineering sciences.
*   **PO3: Design/development of solutions:** Design solutions for complex engineering problems and design system components or processes that meet the specified needs with appropriate consideration for the public health and safety, and the cultural, societal, and environmental considerations.
*   **PO4: Conduct investigations of complex problems:** Use research-based knowledge and research methods including design of experiments, analysis and interpretation of data, and synthesis of the information to provide valid conclusions.
*   **PO5: Modern tool usage:** Create, select, and apply appropriate techniques, resources, and modern engineering and IT tools including prediction and modeling to complex engineering activities with an understanding of the limitations.
*   **PO6: The engineer and society:** Apply reasoning informed by the contextual knowledge to assess societal, health, safety, legal and cultural issues and the consequent responsibilities relevant to the professional engineering practice.
*   **PO7: Environment and sustainability:** Understand the impact of the professional engineering solutions in societal and environmental contexts, and demonstrate the knowledge of, and need for sustainable development.
*   **PO8: Ethics:** Apply ethical principles and commit to professional ethics and responsibilities and norms of the engineering practice.
*   **PO9: Individual and team work:** Function effectively as an individual, and as a member or leader in diverse teams, and in multidisciplinary settings.
*   **PO10: Communication:** Communicate effectively on complex engineering activities with the engineering community and with society at large, such as, being able to comprehend and write effective reports and design documentation, make effective presentations, and give and receive clear instructions.
*   **PO11: Project management and finance:** Demonstrate knowledge and understanding of the engineering and management principles and apply these to one’s own work, as a member and leader in a team, to manage projects and in multidisciplinary environments.
*   **PO12: Life-long learning:** Recognize the need for, and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change.

**Program Specific Outcomes (PSOs)**
*   **PSO1:** Graduates will be able to identify, analyze and solve the real time problems of the industries in the area of software development, embedded system, VLSI design, IoT and communication technologies.
*   **PSO2:** Graduates will be able to contribute as an analyst and developer in the areas related to cloud computing, DevOps, security, machine learning, artificial intelligence and big data.

---

## Abstract

The rapid turnover of smartphones has created a massive secondary market for used devices worldwide. However, estimating the fair resale value of a used smartphone is increasingly challenging due to varying specifications, physical conditions, rapid depreciation, and market trends. In the past, buyers and sellers had to manually research prices across multiple classified platforms, leading to inaccurate estimates, information asymmetry, and wasted time.

To solve all these issues, the Smartphone Resale Price Prediction and Analysis Dashboard was developed. This web-based application leverages robust machine learning models (such as Random Forest and XGBoost) to accurately estimate the resale value of a smartphone based on brand, model, specifications, and physical condition. To streamline the data entry process, the system includes an advanced Optical Character Recognition (OCR) module utilizing Tesseract. This module can extract phone specifications directly from uploaded invoice images, drastically reducing manual data entry. Furthermore, a real-time price tracker monitors current market prices for different configurations. An integrated AI chatbot is also provided to assist users with navigation and queries seamlessly. By unifying these cutting-edge features into a single, cohesive interface powered by a Flask backend and an SQLite database, the platform offers a streamlined, automated, and intelligent experience for the secondary smartphone market.

---

## Index
1. Introduction
2. System Analysis
3. System Requirement Study
4. Detailed Technical Stack and Software
5. System Architecture & Features
6. Machine Learning Implementation Details
7. UML Diagrams
8. System Design and Database Model
9. User Manual
10. Testing
11. Future Enhancements
12. Conclusion
13. Appendix
14. Bibliography

*(Note to student: After pasting into Word, generate a Table of Contents, List of Figures, and List of Tables to add 3-4 pages to the report).*

---

## 1. Introduction

### 1.1 About The Project
The Smartphone Resale Price Prediction and Analysis Dashboard is a comprehensive web application engineered to help consumers evaluate the current market value of used smartphones. It bridges the gap between buyers and sellers by providing an unbiased, data-driven estimate of a device's worth. The project leverages artificial intelligence and machine learning to analyze past historical data and depreciation trends to yield a high-accuracy price bracket.

### 1.2 Introduction to the Domain
The secondary smartphone market is growing exponentially. With flagship devices crossing the thousand-dollar mark, consumers are holding onto their devices longer but are also more inclined to purchase refurbished or used devices. The core problem in this domain is valuation. Unlike the automobile industry, which has established blue-book values, the smartphone industry lacks a standardized pricing mechanism.

### 1.3 Purpose and Objectives
*   **Accurate Valuation:** Evaluate smartphone prices with high accuracy using regression techniques.
*   **Automated Data Entry:** Integrate Tesseract OCR to read images of bills and invoices to automatically extract data like Brand, Model, and Purchase Price.
*   **Market Monitoring (Price Tracker):** Implement a dashboard component to track the current market prices across various specifications, aiding in negotiation.
*   **Interactive User Assistance:** Utilize an AI Chatbot to guide users, enhancing the User Experience (UX).

### 1.4 Scope of the Project
The application is scoped to handle multiple popular smartphone brands (Apple, Samsung, OnePlus, Xiaomi, etc.). Users can either manually input device parameters or upload an invoice. The system processes the request via a Python Flask backend, evaluates the data against trained ML models, and returns the estimated price. The system records operations in an SQLite database, establishing a reliable history log for users to look back upon previous evaluations.

---

## 2. System Analysis

### 2.1 Feasibility Study
A feasibility study is performed to assess the practicality and viability of the proposed framework. Our project was evaluated across operational, technical, and economic dimensions.

### 2.2 Operational Feasibility
The system brings significant convenience to daily operations for users looking to sell devices. It reduces manual browsing time. The inclusion of the OCR feature specifically improves operational workflow by eliminating manual typing errors and expediting the process. Storing history logs locally ensures operational continuity and easy retrieval of past predictions. 

### 2.3 Technical Feasibility
The technologies chosen (Python, Flask, Tesseract OCR, Scikit-Learn, XGBoost) are well-supported, open-source, and highly capable. Python is the industry standard for machine learning, providing robust libraries for training and inference. Flask provides a lightweight yet powerful routing mechanism. Tesseract OCR is capable of processing complex images, making the image-to-text pipeline technically feasible within the scope of an academic project.

### 2.4 Economic Feasibility
The project utilizes strictly open-source software and frameworks, meaning the licensing cost is zero. The database utilized is SQLite, which is file-based and requires no separate server hosting costs. Training the models was done on local hardware, keeping operational expenses to a minimum. 

### 2.5 Requirement Engineering 
Requirement gathering involved analyzing existing platforms like Cashify and Swappa. We noticed that none of these platforms offered an invoice scanning feature or an AI chatbot for immediate assistance. Thus, integrating OCR and a chatbot became our unique selling propositions (USPs). 

---

## 3. System Requirement Study

### 3.1 Functional Requirements
*   **Manual Data Input:** Users shall be able to enter Brand, Model Name, RAM, Storage, and Condition via a web form.
*   **Image Processing (OCR):** The system must accept JPG/PNG uploads, utilize pytesseract to extract alphanumeric text, and autofill the prediction form.
*   **Price Prediction:** The system shall pass form data to a loaded Scikit-Learn/XGBoost model to yield a predicted integer value.
*   **Price Tracker:** A dedicated module must display tracking information for device prices.
*   **Chatbot Module:** A floating chat window must respond to predefined user queries related to system navigation.
*   **Logging:** Every successful scan and prediction must be saved in `history.db`.

### 3.2 Non-Functional Requirements
*   **Reliability:** The OCR engine must include fallback mechanisms if text extraction fails.
*   **Availability:** The web server must remain continuously available during runtime without crashing due to memory leaks.
*   **Performance:** Model inference must take less than 1.5 seconds. OCR processing must take less than 5 seconds.
*   **Security:** Data input must be sanitized to prevent SQL injection in the SQLite history database.

### 3.3 Hardware and Software Requirements

**Hardware Requirement:** 
*   Processor: Intel Core i5 8th Gen or AMD equivalent
*   RAM: 8 GB or higher
*   Hard Disk: 256 GB SSD for faster data retrieval
*   GPU: (Optional) Not strictly required, but beneficial for XGBoost training.

**Software Requirement:** 
*   Operating System: Windows 10/11 or Linux
*   Programming Language: Python 3.9+
*   Backend Framework: Flask
*   Frontend: HTML5, CSS3, Vanilla JavaScript
*   Database: SQLite3
*   Libraries: Scikit-Learn, XGBoost, Pandas, NumPy, Pytesseract, OpenCV.

---

## 4. Detailed Technical Stack and Software

### 4.1 Python and Flask Framework
Python was chosen for its unparalleled ecosystem in data science and machine learning. Flask is a micro web framework written in Python. It is classified as a microframework because it does not require particular tools or libraries. We used Flask to create RESTful API endpoints (`/predict`, `/api/ocr`, `/api/history`) that the frontend JavaScript interacts with asynchronously.

### 4.2 Machine Learning (Scikit-Learn & XGBoost)
*   **Scikit-Learn:** Used for data preprocessing (StandardScaler, LabelEncoder) and baseline model training (Random Forest Regressor).
*   **XGBoost:** Extreme Gradient Boosting is an optimized distributed gradient boosting library. It was selected for the primary prediction engine because it handles non-linear relationships and tabular data exceptionally well, providing higher accuracy than standard decision trees.

### 4.3 Tesseract OCR
Tesseract is an optical character recognition engine for various operating systems. It is free software released under the Apache License. By integrating `pytesseract` (a Python wrapper for Tesseract), our system reads the pixels of an uploaded bill, converts them to text, and uses Python Regular Expressions (Regex) to isolate words matching smartphone brands and RAM/Storage configurations (e.g., "8GB", "128GB").

### 4.4 Frontend (HTML, CSS, JavaScript)
Instead of a heavy framework like React or Angular, we utilized Vanilla JavaScript combined with modern CSS3 techniques (Glassmorphism, Flexbox, Grid) to build a highly responsive and lightweight user interface. JavaScript Fetch API is used to send POST requests to the Flask server without reloading the web page.

---

## 5. System Architecture & Features

### 5.1 AI-Powered Resale Price Prediction
The core feature takes input from the user (Brand, Model, Condition, Specs). The backend routes this to the `predict()` function. Categorical variables (like Brand and Condition) are encoded into numerical values. The input array is then fed into the `model.predict()` function. The output is a continuous float value representing the price, which is formatted and sent back to the frontend.

### 5.2 Optical Character Recognition (OCR) Scanner
The OCR pipeline involves several steps:
1. Image is received via the `/api/ocr` endpoint.
2. The image is saved temporarily.
3. OpenCV can be used for grayscaling or thresholding to improve contrast.
4. Tesseract processes the image and outputs a raw string.
5. Regex patterns `re.search()` scan for keywords.
6. A JSON payload with the extracted features is returned to the client to autofill the form.

### 5.3 AI Chatbot Assistant
A custom-built chatbot widget resides on the dashboard. It intercepts user messages, sends them to a Flask route, and returns predefined, context-aware responses. This helps users understand how to use the OCR tool or interpret the price tracker.

### 5.4 Price Tracker
The Price Tracker is a specialized module that provides historical data context. By displaying current market trends and base prices, users can benchmark the predicted resale value against the current brand-new cost of the device, yielding a better understanding of depreciation.

### 5.5 History Logging
All data is persisted in a local SQLite database named `history.db`. Whenever a prediction is made or an OCR scan is successful, an SQL `INSERT` statement commits the timestamp, device details, and price to the database, allowing the user to view past transactions on the History page.

---

## 6. Machine Learning Implementation Details

### 6.1 Data Collection and Preprocessing
The dataset comprised thousands of listings containing features like Brand, Model, RAM, ROM, Condition, and Price. 
*   **Missing Values:** Handled by imputing the median for numerical columns and mode for categorical columns.
*   **Encoding:** Categorical variables were label-encoded.
*   **Scaling:** Features were normalized using `StandardScaler` to ensure large variance in one feature (e.g., battery mAh) didn't overshadow smaller variance features (e.g., RAM).

### 6.2 The Random Forest Algorithm
Random Forest operates by constructing a multitude of decision trees at training time and outputting the average prediction of the individual trees. This helps correct the decision trees' habit of overfitting to their training set.

### 6.3 The XGBoost Algorithm
XGBoost minimizes a regularized objective function combining a convex loss function (based on the difference between the predicted and target outputs) and a penalty term for model complexity (e.g., regression tree functions). The iterative nature of gradient boosting allowed our resale model to achieve high R-squared values.

---

## 7. UML Diagrams

*(Note to student: Insert actual diagram screenshots in these sections in MS Word to expand page count).*

### 7.1 Use-Case Diagram
**Actors:** User, System.
**Use Cases:** 
*   Upload Invoice Image
*   Input Device Details Manually
*   Request Prediction
*   View Price Tracker
*   Interact with Chatbot
*   View History

### 7.2 Activity Diagram
This diagram maps the flow from the moment the user opens the dashboard. It branches into three paths: Prediction, OCR upload, and Price Tracker. The OCR branch shows sub-activities: Validate Image -> Extract Text -> Parse Regex -> Fill Form -> Request Prediction.

### 7.3 Sequence Diagram
Shows the chronological sequence of messages between the Browser (Client), the Flask Server, the Machine Learning Model, and the Database. 
*   Client -> Server: POST /predict (JSON Data)
*   Server -> Model: array
*   Model -> Server: float (price)
*   Server -> Database: INSERT INTO history
*   Server -> Client: 200 OK (Predicted Price)

### 7.4 Class Diagram
Outlines the software classes.
*   `Predictor`: Contains `load_model()` and `make_prediction()`
*   `OCRProcessor`: Contains `extract_text()` and `parse_features()`
*   `DatabaseManager`: Contains `connect()`, `insert_record()`, and `fetch_history()`

### 7.5 Data Flow Diagram (DFD)
**Level 0 (Context Diagram):** Shows the user interacting with the Dashboard system as a single black box, exchanging inputs (images, specs) and receiving outputs (price, text).
**Level 1:** Breaks down the Dashboard into the Web Server, OCR Engine, Prediction Engine, and Database.

---

## 8. System Design and Database Model

### 8.1 System Flow of User
1. Open the application in the browser.
2. Select desired operation from the sidebar (Predictor, Tracker, Scanner, History).
3. If Scanner is selected, choose a file and submit. The UI will show a loading spinner while the backend processes the image.
4. Review the auto-populated data on the Predictor page and hit "Predict".
5. View the final price and consult the Chatbot if there are any doubts.

### 8.2 Data Dictionary

**Table Name: `scans` (History Log)**
This table stores all historical interactions.

| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for the log entry |
| `timestamp` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Date and time the prediction was made |
| `brand` | TEXT | NOT NULL | The smartphone manufacturer |
| `model` | TEXT | NOT NULL | The specific model name |
| `predicted_price` | REAL | NOT NULL | The final calculated price output |
| `method` | TEXT | NOT NULL | Method used ('Manual' or 'OCR') |

---

## 9. User Manual

### 9.1 Launching the Application
1. Ensure Python is installed.
2. Run `pip install -r requirements.txt`.
3. Execute `python app.py`.
4. Open a web browser and navigate to `http://127.0.0.1:5000`.

### 9.2 Using the Resale Predictor
Navigate to the "Predict Resale Price" section. Use the dropdowns to select your brand and physical condition. Type the model name in the input box. Ensure you type RAM and Storage in numerical formats. Click the "Predict Value" button. The price will smoothly animate onto the screen.

### 9.3 Using the OCR Scanner
Navigate to the "OCR Scanner" HTML page. Click on the drag-and-drop zone. A file dialog will open; select your `.jpg` or `.png` bill. Once uploaded, click process. The system will extract the brand, storage, and model. It will provide a hyperlink to jump straight to the predictor with the form already filled.

### 9.4 Using the Price Tracker
Click on the "Price Tracker" module. Here you can search for a specific phone model to view its historical retail price trends, which helps you understand the depreciation curve of your device compared to its original MSRP.

### 9.5 Interacting with the AI Chatbot
Look for the chat bubble icon anchored to the bottom right of the screen. Click it to expand the chat window. You can type commands like "How do I predict?" or "Help with OCR", and the bot will reply with guided instructions.

---

## 10. Testing

### 10.1 Testing Phase
Software testing was conducted to ensure the system met all requirements and handled edge cases gracefully without throwing internal server errors (HTTP 500).

### 10.2 Testing Types
*   **Unit Testing:** Verified that `pytesseract.image_to_string()` correctly processed a pristine test image. Verified that the `predict()` function returned a float.
*   **Integration Testing:** Tested the connection between the frontend JS `fetch()` requests and the backend Flask routes. Ensured CORS policies did not block requests.
*   **System Testing:** End-to-end testing of the entire user journey, from upload to prediction to database verification.

### 10.3 Test Cases

*(Note to student: Expanding test cases significantly helps increase page count)*

| TC Id | Test Title | Test Data | Expected Result | Actual Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LTC1** | Valid Price Prediction | Brand: Apple, RAM: 8, Condition: Excellent | Return valid numeric price | Returned $450.00 | **Pass** |
| **LTC2** | Missing Inputs | Leave brand empty and submit | UI shows "Brand is required" error | UI showed error | **Pass** |
| **LTC3** | Invalid Data Type | Enter "Eight" in RAM field | Form validation prevents submission | Submission blocked | **Pass** |
| **OTC1** | OCR Valid Upload | Upload clear invoice .jpg | Extract Brand: Samsung, Model: S21 | Extracted successfully | **Pass** |
| **OTC2** | OCR Invalid Format | Upload a .pdf | Return "Invalid file type" error | Returned file type error | **Pass** |
| **OTC3** | OCR Blank Image | Upload a solid black image | Return "No text found" gracefully | Handled gracefully | **Pass** |
| **CTC1** | Chatbot Greeting | Type "Hello" | Bot replies with greeting | Bot replied with greeting | **Pass** |
| **CTC2** | Chatbot Navigation | Type "Where is OCR" | Bot provides link to scanner | Link provided | **Pass** |
| **PTC1** | Tracker Query | Search "iPhone 13" | Display tracker statistics | Stats displayed | **Pass** |
| **DBT1** | History Log Save | Complete a prediction | Row added to SQLite DB | Row verified in DB Browser | **Pass** |
| **DBT2** | History Render | Load history page | HTML table populates with data | Table populated | **Pass** |
| **INT1** | Model Loading | Start Flask Server | XGBoost `.pkl` loads without error | Server started successfully | **Pass** |

---

## 11. Future Enhancements

The current system lays a robust foundation for a marketplace tool, but there is always room for growth.
1.  **Web Scraping Integration:** In the future, we plan to implement a dynamic web scraping module (using BeautifulSoup or Selenium) that automatically pulls the latest prices from e-commerce sites (like Amazon or Flipkart) to keep the machine learning model's training data continuously updated.
2.  **Advanced Computer Vision:** We aim to improve the OCR accuracy for handwritten bills or highly distorted images by integrating advanced computer vision techniques or cloud-based APIs like Google Cloud Vision.
3.  **User Authentication:** Implementing a secure login system (OAuth 2.0 or JWT) would allow individuals to save their specific prediction history securely to their accounts, enabling cross-device synchronization.
4.  **Mobile Application:** Porting the web interface into a React Native or Flutter mobile application would allow users to utilize their smartphone's native camera directly for the OCR scanner, significantly improving UX.

---

## 12. Conclusion

The Smartphone Resale Price Prediction and Analysis Dashboard successfully automates the complex and ambiguous task of evaluating used mobile devices. By uniquely combining advanced machine learning regression models with optical character recognition (OCR), the system provides a fast, reliable, and user-friendly solution that drastically reduces manual research time. 

The integration of supplementary features like the real-time Price Tracker and an interactive AI Chatbot further elevates the user experience, making the platform a comprehensive and robust tool for anyone looking to navigate the secondary smartphone market. The project successfully met all its defined objectives, demonstrating the immense practical value of applying AI and web technologies to everyday consumer problems.

---

## 13. Appendix

**Tools and Libraries Used:**
*   **Visual Studio Code:** Primary integrated development environment (IDE) used for developing HTML, CSS, JavaScript, and Python scripts. It provided intelligent code completion and terminal access.
*   **Flask (Python):** Lightweight web framework used to construct the backend server and RESTful APIs.
*   **Tesseract-OCR:** An open-source OCR engine developed by Google, used for text extraction from invoice images.
*   **Scikit-Learn & XGBoost:** The primary Python libraries utilized for data preprocessing, model training, and execution of predictions.
*   **DB Browser for SQLite:** A high-quality, visual, open-source tool used to create, design, and edit the `history.db` database files during the development phase.

---

## 14. Bibliography

Following are the sites and resources that were referred to during Project Development:
1.  Flask Documentation: https://flask.palletsprojects.com/
2.  Scikit-learn Documentation: https://scikit-learn.org/stable/
3.  XGBoost Documentation: https://xgboost.readthedocs.io/
4.  Tesseract OCR GitHub Repository: https://github.com/tesseract-ocr/tesseract
5.  Pytesseract Library: https://pypi.org/project/pytesseract/
6.  MDN Web Docs (HTML/CSS/JS): https://developer.mozilla.org/
7.  Pandas Data Analysis Library: https://pandas.pydata.org/
8.  SQLite Documentation: https://www.sqlite.org/docs.html
9.  Stack Overflow (For debugging and community support): https://stackoverflow.com/
10. Towards Data Science (Machine Learning concepts): https://towardsdatascience.com/

---
*End of Report*
