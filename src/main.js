

document.addEventListener('DOMContentLoaded', () => {
  // Password Toggle Logic
  const togglePassword = document.querySelector('#togglePassword');
  const passwordInput = document.querySelector('#password');

  if (togglePassword && passwordInput) {
    togglePassword.addEventListener('click', function () {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      
      // Toggle icon
      if (type === 'text') {
        this.classList.remove('fa-eye');
        this.classList.add('fa-eye-slash');
      } else {
        this.classList.remove('fa-eye-slash');
        this.classList.add('fa-eye');
      }
    });
  }

  // Theme Toggle Logic
  const themeToggle = document.querySelector('#themeToggle');
  
  // Initialize theme from localStorage
  if (localStorage.getItem('theme') === 'light') {
    document.body.classList.add('light-theme');
    if (themeToggle) {
      themeToggle.classList.replace('fa-moon', 'fa-sun');
    }
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-theme');
      
      const isLight = document.body.classList.contains('light-theme');
      if (isLight) {
        localStorage.setItem('theme', 'light');
        themeToggle.classList.replace('fa-moon', 'fa-sun');
      } else {
        localStorage.setItem('theme', 'dark');
        themeToggle.classList.replace('fa-sun', 'fa-moon');
      }
    });
  }

  // Sidebar Menu Active State
  const menuLinks = document.querySelectorAll('.menu-link');
  menuLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      if (this.getAttribute('href') === '#') {
        e.preventDefault(); // Prevent default if it's a dummy link
      }
      menuLinks.forEach(l => l.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // AI Chatbot Logic
  const chatbotToggle = document.getElementById('chatbotToggle');
  const chatbotWindow = document.getElementById('chatbotWindow');
  const chatbotClose = document.getElementById('chatbotClose');
  const chatbotInput = document.getElementById('chatbotInput');
  const chatbotSend = document.getElementById('chatbotSend');
  const chatbotMessages = document.getElementById('chatbotMessages');

  if (chatbotToggle && chatbotWindow) {
    // Open/Close chat window
    chatbotToggle.addEventListener('click', () => {
      chatbotWindow.classList.toggle('open');
      if (chatbotWindow.classList.contains('open')) {
        chatbotInput.focus();
      }
    });

    chatbotClose.addEventListener('click', () => {
      chatbotWindow.classList.remove('open');
    });

    // Helper to add message to UI
    function addMessage(text, isUser = false) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
      
      const contentDiv = document.createElement('div');
      contentDiv.className = 'message-content';
      contentDiv.textContent = text;
      
      msgDiv.appendChild(contentDiv);
      chatbotMessages.appendChild(msgDiv);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight; // auto-scroll
    }

    // Handle sending message
    function handleSendMessage() {
      const text = chatbotInput.value.trim();
      if (!text) return;
      
      // 1. Add user message
      addMessage(text, true);
      chatbotInput.value = '';
      
      // 2. Simulate AI Typing delay and response
      setTimeout(() => {
        const lowerText = text.toLowerCase();
        let aiResponse = "I'm a virtual assistant for the Price Predict AI. You can ask me about how our machine learning models work, phone depreciation, specific brands like Apple or Samsung, or how to use the dashboard!";
        
        // Advanced mock intelligence
        if (lowerText.includes('price of') || lowerText.includes('how much') || lowerText.includes('current price') || lowerText.includes('resale price') || lowerText.includes('cost of') || lowerText.includes('value of')) {
          aiResponse = "To get the most accurate price estimate, please use our dedicated tools! Head over to the 'Resale Price' tab to predict a phone's second-hand value, or use the 'Price Tracker' tab to check current market prices.";
        } else if (lowerText.includes('how') && (lowerText.includes('model') || lowerText.includes('work') || lowerText.includes('predict'))) {
          aiResponse = "Our system uses two powerful machine learning models. For Resale Price, we use a Random Forest Classifier trained on 1 million records to group your phone into a value tier, then apply custom depreciation logic. For Current Price, we use a similar architecture to analyze specs!";
        } else if (lowerText.includes('iphone') || lowerText.includes('apple')) {
          aiResponse = "Apple iPhones generally hold their resale value much better than Android counterparts, depreciating at roughly 2-3% per month in the first year. We validate Apple inputs strictly to ensure they use iOS and Apple Silicon (A-series chips).";
        } else if (lowerText.includes('samsung') || lowerText.includes('galaxy')) {
          aiResponse = "Samsung Galaxy S and Z series phones are great, but they often see a steeper depreciation curve than iPhones in the second-hand market. Our model accounts for this in the price banding.";
        } else if (lowerText.includes('depreciation') || lowerText.includes('value drop')) {
          aiResponse = "Depreciation is calculated using a baseline of roughly 2.5% per month, but this is adjusted based on battery health, screen condition, body damage, repair history, and water damage.";
        } else if (lowerText.includes('error') || lowerText.includes('not working') || lowerText.includes('fix')) {
          aiResponse = "If you're seeing an error, make sure all fields are filled out correctly! Our validation engine will reject combinations that don't make sense (like an Apple phone running Android).";
        } else if (lowerText.includes('hello') || lowerText.includes('hi ') || lowerText.trim() === 'hi') {
          aiResponse = "Hello! I'm the Price Predict AI assistant. How can I help you today? Try asking me about 'depreciation' or 'how the model works'!";
        } else if (lowerText.includes('thank')) {
          aiResponse = "You're very welcome! Let me know if you need anything else.";
        } else if (lowerText.includes('who are you') || lowerText.includes('what are you')) {
          aiResponse = "I am the intelligent chatbot assistant built into the Price Predict dashboard, designed to help you understand our predictive models and navigate the platform.";
        } else if (lowerText.includes('accuracy') || lowerText.includes('accurate')) {
          aiResponse = "Our Resale Price model (Random Forest) achieves over 90% classification accuracy on the test data! It takes 27 different features into account to give you the most precise estimate possible.";
        } else if (lowerText.includes('ocr') || lowerText.includes('scanner')) {
          aiResponse = "The OCR Scanner uses Tesseract and OpenCV to automatically extract the phone brand, model, and purchase price from an uploaded invoice or box picture. It saves you from typing everything manually!";
        } else if (lowerText.includes('still learning')) {
          aiResponse = "Not anymore! I've been fully upgraded to answer all your questions about our predictive models and platform features.";
        }
        
        addMessage(aiResponse, false);
      }, 800);
    }

    chatbotSend.addEventListener('click', handleSendMessage);
    chatbotInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSendMessage();
    });
  }

  // Set User Profile from localStorage
  const userFullname = localStorage.getItem('userFullname');
  if (userFullname) {
    const userNameElements = document.querySelectorAll('.user-name');
    const userAvatarElements = document.querySelectorAll('.user-avatar');
    
    userNameElements.forEach(el => el.textContent = userFullname);
    
    // Get initials for avatar (first letter of up to two words)
    const words = userFullname.split(' ').filter(w => w.length > 0);
    let initials = '';
    if (words.length > 0) initials += words[0][0];
    if (words.length > 1) initials += words[1][0];
    initials = initials.toUpperCase();
    
    userAvatarElements.forEach(el => el.textContent = initials);
  }
});
